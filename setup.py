#!/usr/bin/env python

from distutils.core import setup

setup(name='l20n',
      version='0.2',
      description='Python L20n library',
      author='Mozilla',
      author_email='team@mozilla.org',
      url='https://github.com/l20n/python-l20n',
      packages=['ftl', 'ftl.format'],
      install_requires=[
          'six'
      ]
      )
