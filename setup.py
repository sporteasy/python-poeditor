#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages

import poeditor


install_requires = []
dependency_links = []

# Inject requirements from requirements.txt into setup.py
filename = 'requirements.txt'
requirements_file = parse_requirements(filename, session=PipSession())
for req in requirements_file:
    install_requires.append(str(req.req))
    if req.link:
        dependency_links.append(str(req.link))

setup(
    name='poeditor',
    version=poeditor.__version__,
    packages=find_packages(),
    author="Charles Vallantin Dulac",
    author_email="charles.vdulac@gmail.com",
    description="Client Interface for POEditor API (https://poeditor.com).",
    long_description=open('README.rst').read(),
    include_package_data=True,
    url='https://github.com/sporteasy/python-poeditor',
    classifiers=[
        "Development Status :: 1 - Planning",
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        "Topic :: Software Development :: Localization",
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,
    license='MIT',
    test_suite="nose.collector",
)
