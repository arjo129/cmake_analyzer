#!/usr/bin/env python3

from distutils.core import setup

setup(name='cmake_analyzer',
      version='0.1',
      description='A static analysis tool for cmake files',
      author='Arjo Chakravarty',
      author_email='arjo@openrobotics.org',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['cmake_analyzer'],
      package_dir={'cmake_analyzer': 'cmake_analyzer'},
      test_suite="tests"
    )