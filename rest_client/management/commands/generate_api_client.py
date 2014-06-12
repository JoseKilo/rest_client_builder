# Copyright 2013 Rockabox Media. All Rights Reserved.

"""
manage.py command that generates a client library package with an
endpoints.py module inside to be used by a client python project.

Inspired by django-extensions management command `show_urls`
https://github.com/django-extensions/django-extensions
"""

import ast
from distutils import core
import imp
import inspect
import json
import os
import re
import shutil
import sys

from django.core.exceptions import ViewDoesNotExist
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.core.management.base import BaseCommand, CommandError

from rest_client import unparse


def extract_info_from_urlpatterns(urlpatterns, url_base='', name_base=''):
    """
    Obtain information about every pattern on input URL patterns

    Iterates over urlpatterns list. If it finds an include, it recurses
    into it. Found patterns are returned in a list of 3-tuples structure.
    The 3-tuples includes view (callback), url and name information.
    """
    info = []
    for urlpattern in urlpatterns:
        try:
            if isinstance(urlpattern, RegexURLPattern):

                name = urlpattern.name
                if name_base:
                    name = name_base + ':' + urlpattern.name

                info.append((urlpattern.callback,
                            url_base + urlpattern.regex.pattern,
                            name))

            elif (isinstance(urlpattern, RegexURLResolver) or
                  hasattr(urlpattern, 'url_patterns')):

                patterns = urlpattern.url_patterns

                if name_base and urlpattern.namespace:
                    namespace = name_base + ':' + urlpattern.namespace
                elif name_base:
                    namespace = name_base
                elif urlpattern.namespace:
                    namespace = urlpattern.namespace

                info.extend(extract_info_from_urlpatterns(
                    patterns, url_base + urlpattern.regex.pattern, namespace))
            else:
                raise TypeError('{} does not appear to be a '
                                'urlpattern object'.format(urlpattern))

        except (ViewDoesNotExist, ImportError):
            continue
    return info


def clean_patterns(urls_data):
    ret = []
    for _, pattern, name in urls_data:
        pattern = re.sub(r'\(\?P<', '{', pattern)
        pattern = re.sub(r'>', '}', pattern)
        pattern = filter(lambda c: c not in '+^$()[]', pattern)
        pattern = re.sub('//', '/', pattern)

        name = re.sub('-', '_', name)
        name = re.sub(':', '__', name)

        ret.append((name, pattern))
    return ret


class Command(BaseCommand):
    args = '[root_urls.py]'
    help = 'Generate client library'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError(
                'Usage:\n'
                'python manage.py generate_api_client '
                '[root_urls.py] [package_name] [package_version]'
            )

        conf = {
            'NAME': args[1],
            'VERSION': args[2]
        }

        root_urls_module = imp.load_source('urls', args[0])

        base_dir = self.create_client_package_base_dir()
        self.copy_base_client_library(base_dir, conf)
        self.write_endpoints(root_urls_module, base_dir, conf)
        setup_file = self.copy_setup(base_dir, conf)
        self.replace_macros(setup_file, conf)
        self.run_setup(base_dir)

    def replace_macros(self, setup_path, conf):
        class MacroReplacer(ast.NodeTransformer):
            def visit_Str(self, node):
                if node.s.startswith('__') and node.s.endswith('__'):
                    conf_key = re.sub('__', '', node.s)
                    conf_value = conf.get(conf_key, conf_key)
                    return ast.Str(conf_value)
                else:
                    return ast.Str(node.s)
        with open(setup_path, 'r') as setup_file:
            setup_content = setup_file.read()
        original_setup = ast.parse(setup_content)
        modified_setup = MacroReplacer().visit(original_setup)
        with open(setup_path, 'w') as setup_file:
            unparse.Unparser(modified_setup, setup_file)

    def run_setup(self, base_dir):
        previous_path = os.getcwd()
        os.chdir(base_dir)
        core.run_setup('setup.py', ['sdist'])
        os.chdir(previous_path)

    def copy_setup(self, base_dir, conf):
        setup_path = os.path.join(base_dir, conf['NAME'], 'setup_template.py')
        destination = os.path.join(base_dir, 'setup.py')
        shutil.copy(setup_path, destination)
        return destination

    def create_client_package_base_dir(self):
        base_dir_path = '_rest_client_build'
        if not os.path.exists(base_dir_path):
            os.makedirs(base_dir_path)
        return base_dir_path

    def copy_base_client_library(self, base_dir, conf):
        base_dir_abs = os.path.abspath(base_dir)
        module = __import__('rest_client')
        init_path = inspect.getsourcefile(module)
        module_path = os.path.sep.join(init_path.split(os.path.sep)[:-1])
        shutil.rmtree(base_dir)
        shutil.copytree(module_path, os.path.join(base_dir, conf['NAME']))

    def write_endpoints(self, root_urls_module, base_dir, conf):
        urls = root_urls_module.urlpatterns
        urls_data = extract_info_from_urlpatterns(urls,
                                                  url_base='api/',
                                                  name_base='')
        clean_urls = clean_patterns(urls_data)
        ENDPOINTS = dict(clean_urls)

        endpoints_path = os.path.join(base_dir, conf['NAME'], 'endpoints.py')

        with open(endpoints_path, 'w+') as output_module:
            output_module.write('ENDPOINTS = ')
            output_module.write(json.dumps(ENDPOINTS, sort_keys=True,
                                           indent=4, separators=(',', ': ')))
            output_module.write('\n')
