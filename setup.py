#!/usr/bin/env python3
from distutils.core import setup
setup(
   name = 'steam',
   packages = ['steam'],
   version = '1.0.2',
   description = 'A Steam API',
   author 'Evan Young',
   url = 'https://github.com/DocCodes/steam',
   download_url = 'https://github.com/DocCodes/steam/archive/master.tar.gz',
   keywords = ['steam', 'api', 'userdata'],
   classifiers = [
      'Development Status :: 5 - Production',
      'Intended Audience :: Deevelopers',
      'Topic :: Steam User API',
      'License :: GNUGLPv3',
      'Programming Language :: Python :: 3.6'
   ],
   install_requires = [
      'requests',
      'beautifulsoup4'
   ],
   python_requires = '~=3.6'
)
