# steam
A Python API for Steam userdata

## How-To Use
```
import steam

evan = steam.user(76561198069463927) # My Steam account, provided in SteamID64
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
