#!/usr/bin/env python

from setuptools import setup

setup(name='l20n',
      version='4.0.0a1',
      description='Python L20n library',
      author='Zibi Braniecki',
      author_email='gandalf@mozilla.com',
      url='https://github.com/l20n/python-l20n',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
      ],
      packages=['l20n', 'l20n.format'],
      install_requires=[
          'six'
      ]
      )
