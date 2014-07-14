#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='__NAME__',
    version='__VERSION__',
    author='rockabox',
    author_email='tech@rockabox.com',
    packages=['__BASE_PACKAGE__'],
    include_package_data=True,
    url='https://github.com/rockabox/rest_client_builder',
    license='MIT',
    description='Rest Client',
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests==2.3.0',
    ],
)
