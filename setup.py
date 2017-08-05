#!/usr/bin/env python3
from distutils.core import setup
setup(
   name = 'wemo',
   packages = ['wemo'],
   version = '1.0.0',
   description = 'A Wemo API',
   author = 'Evan Young',
   url = 'https://github.com/DocCodes/wemo',
   download_url = 'https://github.com/DocCodes/wemo/archive/master.tar.gz',
   keywords = ['wemo', 'api', 'automation'],
   classifiers = [
      'Development Status :: 5 - Production',
      'Intended Audience :: Developers',
      'Topic :: Steam User API',
      'License :: GNU GPLv3',
      'Programming Language :: Python :: 3.6'
   ],
   install_requires = [
      'requests'
   ],
   python_requires = '~=3.6'
)
