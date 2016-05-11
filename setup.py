#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='l20n',
      version='0.2',
      description='Python L20n library',
      author='Mozilla',
      author_email='team@mozilla.org',
      url='https://github.com/l20n/python-l20n',
      packages=['l20n', 'l20n.format', 'ftl', 'ftl.format'],
     )

