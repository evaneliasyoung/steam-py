# Steam

[![Build Status](https://travis-ci.org/DocCodes/steam.svg?branch=master)](https://travis-ci.org/DocCodes/steam-py)
[![Documentation Status](http://img.shields.io/badge/docs-v1.3.3-brightgreen.svg?style=flat)](https://github.com/DocCodes/steam-py/wiki)
[![Release](https://img.shields.io/github/release/doccodes/steam.svg)](https://github.com/DocCodes/steam-py/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/steam-py.svg)](https://pypi.python.org/pypi/steam-py/1.3.3)

The time from profile request to usable data is ≈ 3 seconds

## Installation
### Windows
```
pip3 install steam-py
```
### macOS
```
sudo -H pip3 install steam-py
```
### Linux
```
sudo pip3 install steam-py
```

## How-To Use
```
import steam

evan = steam.user(s64='76561198069463927') # My Steam account, provided in SteamID64
print(f'{evan.name} is Level {evan.level}, wow- how sad')
```
output
```
Evan is Level 27, wow- how sad
```
View the wiki for documentation on the user type

## Requirements
Any requirements will automatically be installed using the aforementioned installation method.
To install any modules use `pip3 install (module)`
* requests
* beautifulsoup4
* pytest
