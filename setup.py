#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='l20n',
      version='1.0',
      description='Python L20n library',
      author='Zbigniew Braniecki',
      author_email='zbigniew@braniecki.net',
      url='https://github.com/l20n/python-l20n',
      packages=['lib.l20n.format'],
      package_dir = {
          'l20n': os.path.join('lib'),
      }
     )

