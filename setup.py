#!/usr/bin/env python

import os
from setuptools import setup

setup(
        name = 'rscloud',
        version = '0.2.2',
        author = 'James Bardin',
        author_email = 'jbardin@litl.com',
        license = 'MIT',
        url = 'https://github.com/jbardin/rscloud.git',
        packages = ['rscloud'],
        install_requires = ['requests', 'python-dateutil'],
)
