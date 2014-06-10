# Copyright 2013 Rockabox Media. All Rights Reserved.

"""
manage.py command that generates an endpoints.py module to be used by
a client library.

Inspired by django-extensions management command `show_urls`
https://github.com/django-extensions/django-extensions

"""

import json
import re

from django.core.exceptions import ViewDoesNotExist
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
from django.core.management.base import BaseCommand


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
    args = ''
    help = 'Generate endpoints.py'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        import rbx.api_drf.urls
        urls = rbx.api_drf.urls.urlpatterns
        urls_data = extract_info_from_urlpatterns(urls,
                                                  url_base='api/',
                                                  name_base='')
        clean_urls = clean_patterns(urls_data)
        ENDPOINTS = dict(clean_urls)

        with open('endpoints.py', 'w+') as output_module:
            output_module.write('ENDPOINTS = ')
            output_module.write(json.dumps(ENDPOINTS, sort_keys=True,
                                           indent=4, separators=(',', ': ')))
            output_module.write('\n')
