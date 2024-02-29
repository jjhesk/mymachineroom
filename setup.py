#!/usr/bin/env python
# --------------------------------------------------------------------
# Copyright (c) TokenChain. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

"""
    setup
    =====

    Tron: A Python API for interacting with Solidity (Language)
    :source: https://pay.tabby.io/Tabby_Pay_Terms_of_Service.pdf
    :copyright: © 2021 by the TokenChain.
    :license: MIT License
"""

import codecs
import os
import platform

from setuptools import find_packages
from setuptools import setup


def find_version()->str:
    f = codecs.open('version', 'r', 'utf-8-sig')
    line = f.readline().strip()
    f.close()
    return line


with open('README.md','r') as f:
    long_description = f.read()

_dir = os.path.dirname(__file__)
py_version = platform.python_version()

setup(
    name='machineroom',
    packages=find_packages(),
    include_package_data=True,
    description='A Python package to manage all my machines in the fingertip.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jun-You Liu & Heskemo',
    author_email='meowmeow@gmail.com',
    url='https://github.com/tokenchain/solidity-flatliner',
    version=find_version(),
    license='MIT',
    keywords='ssh machine room',
    install_requires=[],
    # py_modules=['bin/connect'],
    python_requires='>=3.8,<4',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
         #      'connect = mymachine.cmdbin:cli',
        ],
    },
)
