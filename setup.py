#!/usr/bin/env python3
from distutils.core import setup
setup(
    name='steam-py',
    packages=['steam'],
    version='1.4.0',
    description='A Steam API',
    author='Evan Young',
    url='https://github.com/evaneliasyoung/steam-py',
    download_url='https://github.com/evaneliasyoung/steam-py/archive/master.tar.gz',
    keywords=['steam', 'api', 'userdata'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English'
    ],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pytest'
    ],
    python_requires='~=3.7'
)
