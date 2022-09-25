#!/usr/bin/env python3

import codecs
from setuptools import setup

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from pyqtcmd.meta import VERSION, RELEASE


with codecs.getreader('utf-8')(open('README.md', 'rb')) as fileobj:
    README = fileobj.read()


setup(
    name='pyqtcmd',
    version=RELEASE,
    description='PyQt6/PyQt5-based Command implementation for undo/redo',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/fraca7/pyqtcmd',
    author='J\u00e9r\u00f4me Laheurte',
    author_email='jerome@jeromelaheurte.net',
    license='MIT',
    classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    ],
    packages=['pyqtcmd'],
    install_requires=[],
    )
