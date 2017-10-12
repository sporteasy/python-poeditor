#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import poeditor


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
        'Programming Language :: Python :: 3',
        "Topic :: Software Development :: Localization",
    ],
    install_requires=['requests'],
    license='MIT',
    test_suite="nose.collector",
)
