#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='rest_client',
    version='1.0.0',
    author='rockabox',
    author_email='tech@rockabox.com',
    packages=['rest_client', 'rest_client.management.commands'],
    include_package_data=True,
    url='https://github.com/rockabox/rest_client',
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
