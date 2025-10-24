#!/usr/bin/env python3
# Copyright 2025 Arjo Chakravarty
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
import os

# Read the long description from readme file if it exists
long_description = ''
readme_files = ['readme.md', 'README.md', 'README.rst', 'README.txt', 'README']
for readme_file in readme_files:
    readme_path = os.path.join(os.path.dirname(__file__), readme_file)
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            long_description = fh.read()
        break

setup(
    name='cmake_analyzer',
    version='0.1',
    description='A static analysis tool for cmake files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Arjo Chakravarty',
    author_email='arjo@openrobotics.org',
    url='https://github.com/arjo129/cmake_analyzer',
    packages=find_packages(),
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',
    test_suite='tests'
)