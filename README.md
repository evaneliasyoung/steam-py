# Steam

[![Build Status](https://travis-ci.org/DocCodes/steam.svg?branch=master)](https://travis-ci.org/DocCodes/steam)
[![Documentation Status](http://img.shields.io/badge/docs-1.2.1-brightgreen.svg?style=flat)](https://github.com/DocCodes/steam/wiki)
[![Release](https://img.shields.io/badge/release-1.2.1-brightgreen.svg)](https://github.com/DocCodes/steam/releases/latest)
[![Beta](https://img.shields.io/badge/beta-none-blue.svg)](https://github.com/DocCodes/steam)

The time from profile request to usable data is ≈ 3 seconds

## Installation
1. First download this git
2. Change to the steam directory
3. Then use pip3 to install it

### Windows
*See above to obtain code*
```
cd steam
pip3 install .
```
### Linux / macOS
```
cd ~/Downloads
git clone https://github.com/DocCodes/steam
cd steam
sudo -H pip3 install .
```

## How-To Use
```
import steam

evan = steam.user('76561198069463927') # My Steam account, provided in SteamID64
print(f'{evan.name} is Level {evan.level}, wow- how sad')
```
output
```
Evan is Level 27, wow- how sad
```
View the wiki for documentation on the user type

## Requirements
To install any modules use `pip3 install (module)`
* requests
* beautifulsoup4
* pytest
