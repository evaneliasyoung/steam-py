#!/usr/bin/env python3
"""A Steam API written for python without the clunky Steam API
"""
from requests import get as req
from bs4 import BeautifulSoup
from json import loads as jsld
from datetime import datetime as dt
from re import sub as reg
from typing import List, Dict, Optional, Any
from os import system

__author__ = 'Evan Elias Young'
__copyright__ = 'Copyright 2017-2019, Evan Elias Young'
__credits__ = 'Evan Elias Young'

__license__ = 'GNU GPLv3'
__version__ = '1.4.0'
__maintainer__ = 'Evan Elias Young'
__status__ = 'Production'


def RemoveAlls(text: str) -> str: return reg('[\t\r\n]', '', text)


def MakeInt(text: str) -> int: return int(reg('[^0-9]', '', text))


def MakeFloat(text: str) -> float: return float(reg('[^0-9.]', '', text))


class Location:
    """Will return a location object, with various information about the user's location."""

    def __init__(self, url: str, contents: str) -> None:
        self.url: str = url
        self.contents: str = contents


class Status:
    """Will return a status object, with various information about the user's status."""

    def __init__(self, main: str, game: Optional[str], last: Optional[str]) -> None:
        self.main: str = main
        self.game: Optional[str] = game
        self.last: Optional[str] = last


class Badge:
    """Will return a badge object, with various information about each badge."""

    def __init__(self, inst: BeautifulSoup) -> None:
        """Will return a badge object, with various information about each badge."""
        self.inst: BeautifulSoup = inst
        self.title: str = self.getTitle()
        self.game: str = self.getGame()
        self.xp: int = self.getXP()
        self.level: Optional[int] = self.getLevel()
        self.earned: int = self.getEarnTime()

    def getTitle(self) -> str:
        """Will return the title of the card."""
        return str(self.inst.find('div', class_='badge_info_title').text)

    def getGame(self) -> str:
        """Will return the game (or source) of the card."""
        return str(self.inst.find('div', class_='badge_title').text.split('\xa0')[0].strip())

    def getLevel(self) -> Optional[int]:
        """Will return the level of the card."""
        lvlxp: List[str] = RemoveAlls(
            self.inst.find('div', class_='').text).split(',')
        if len(lvlxp) == 2:
            return MakeInt(lvlxp[0])
        return None

    def getXP(self) -> int:
        """Will return the level of the card."""
        lvlxp: List[str] = RemoveAlls(
            self.inst.find('div', class_='').text).split(',')
        if len(lvlxp) == 2:
            return MakeInt(lvlxp[1])
        return MakeInt(lvlxp[0])

    def getEarnTime(self) -> int:
        """Will return the time the user earned the badge."""
        tmp: List[str] = self.inst.find(
            'div', class_='badge_info_unlocked').text.strip().replace('Unlocked ', '').split(' ')
        if len(tmp) == 5:
            return int(dt.strptime(f'{tmp[2]} {tmp[0]} {tmp[1][:-1]:0>2} {tmp[4].upper():0>7}', '%Y %b %d %I:%M%p').timestamp()) * 1000
        return int(dt.strptime(f'{dt.now().year} {tmp[0]} {tmp[1]:0>2} {tmp[3].upper():0>7}', '%Y %b %d %I:%M%p').timestamp()) * 1000


class Game:
    """Will return a game object, with various information about each game."""

    def __init__(self, inst: Dict[str, str]) -> None:
        """Will return a game object, with various information about each game."""
        self.appid: int = int(inst['appid'])
        self.name: str = inst['name']
        self.logo: str = inst['logo']
        self.hours: float = MakeFloat(
            inst['hours_forever']) if 'hours_forever' in inst else 0.0
        self.recent: float = MakeFloat(
            inst['hours']) if 'hours' in inst else 0.0
        self.last: int = int(inst['last_played']) * \
            1000 if 'last_played' in inst else 0


class User:
    """Will return a user object, with various information about the user."""

    def __init__(self, s64: Optional[str] = None, sid: Optional[str] = None) -> None:
        """Will return a user object, with various information about the user."""
        if s64 != None:
            if len(str(s64)) != 17:
                raise Exception('The Steam64 provided is invalid')
            aft = f'profiles/{str(s64)}/'
        elif sid != None:
            aft = f'id/{str(sid)}/'
        else:
            raise Exception('Invalid user parameters')

        self.url: str = f'http://steamcommunity.com/{aft}'
        self.soupMain = BeautifulSoup(req(self.url).text, 'html.parser')
        if 'error' in self.soupMain.title.text.lower():
            raise Exception('Error retrieveing Steam Profile')
        self.soupDate = BeautifulSoup(
            req(f'{self.url}badges/1/').text, 'html.parser')
        self.soupBadges = BeautifulSoup(
            req(f'{self.url}badges/').text, 'html.parser')
        self.soupGames = BeautifulSoup(
            req(f'{self.url}games/?tab=all').text, 'html.parser')
        self.soupWish = BeautifulSoup(
            req(f'{self.url}wishlist/').text, 'html.parser')
        self.private: bool = self.getPrivate()
        self.persona: str = self.getPersona()
        self.avatar: str = self.getAvatar()

        self.name: Optional[str] = self.getName()
        self.created: Optional[int] = self.getCreationTime()
        self.location: Optional[Location] = self.getLocation()
        self.status: Optional[Status] = self.getStatus()
        self.level: Optional[int] = self.getLevel()
        self.counts: Optional[Dict[str, int]] = self.getCounts()
        self.badges: Optional[List[Badge]] = self.getBadges()
        self.favBadge: Optional[Badge] = self.getFavBadge()
        self.games: Optional[Dict[int, Game]] = self.getGames()
        self.recents: Optional[List[Game]] = self.getRecents()
        self.wishlist: Optional[Dict[int, Any]] = self.getWishlist()
        self.aliases: Optional[List[str]] = self.getAliases()

    def printAll(self) -> None:
        """For debugging purposes, prints all the non-callable items in the user object."""
        for a in dir(self):
            if not a.startswith('__') and not a.startswith('soup') and not callable(self.__getattribute__(a)) and a != 'req':
                print(f'{a}: {self.__getattribute__(a)}')
        print()

    def getPrivate(self) -> bool:
        """Will return a bool of whether or not the profile is private."""
        return bool(self.soupMain.find('div', class_='profile_private_info') != None)

    def getPersona(self) -> str:
        """Will return the display-name (persona) of the user."""
        return str(self.soupMain.find('span', class_='actual_persona_name').text)

    def getAliases(self) -> Optional[List[str]]:
        """Will return the past display-names."""
        if self.private:
            return None
        als: List[str] = []
        data: List[Dict[str, str]] = jsld(req(f'{self.url}ajaxaliases/').text)
        for a in data:
            als.append(a['newname'])
        return als

    def getName(self) -> Optional[str]:
        """Will return the name of the user."""
        if self.private:
            return None
        parElem: Optional[BeautifulSoup] = self.soupMain.find(
            'div', class_='header_real_name ellipsis')
        if parElem == None or parElem.find('bdi').text == '':
            return None
        return parElem.find('bdi').text

    def getLocation(self) -> Optional[Location]:
        """Will return the location of the user."""
        if self.private:
            return None
        parElem: Optional[BeautifulSoup] = self.soupMain.find(
            'div', class_='header_real_name ellipsis')
        if parElem == None or parElem.find('img') == None:
            return None
        return Location(parElem.find('img')['src'], parElem.contents[-1].strip())

    def getCreationTime(self) -> Optional[int]:
        """Will return the creation-time of the Steam Profile."""
        if self.private:
            return None
        year: int = int(RemoveAlls(self.soupDate.find(
            'div', class_='badge_description').text)[-5: -1])
        tmp: List[str] = RemoveAlls(self.soupDate.find(
            'div', class_='badge_info_unlocked').text)[9:].split(' ')
        return int(dt.strptime(f'{year} {tmp[0]} {tmp[1]:0>2} {tmp[3].upper():0>7}', '%Y %b %d %I:%M%p').timestamp() * 1000)

    def getAvatar(self) -> str:
        """Will return the url of the avatar of the user."""
        return str(self.soupMain.find('div', class_='playerAvatarAutoSizeInner').find('img')['src'])

    def getStatus(self) -> Optional[Status]:
        """Will return the status of the user."""
        if self.private:
            return None
        mainElem: BeautifulSoup = self.soupMain.find(
            'div', class_='profile_in_game_header')
        descElem: BeautifulSoup = self.soupMain.find(
            'div', class_='profile_in_game_name')
        main: str = mainElem.text.replace('Currently ', '').lower()
        last: Optional[str] = None
        game: Optional[str] = None
        if main == 'offline':
            last = descElem.text.replace('Last Online ', '').lower()
        elif main == 'in-game':
            game = descElem.text
        return Status(main, game, last)

    def getLevel(self) -> int:
        """Will return the Steam level of the user."""
        if self.private:
            return False
        elem: BeautifulSoup = self.soupMain.find('span', class_='friendPlayerLevelNum')
        level: int = MakeInt(elem.text)
        return level

    def getFavBadge(self) -> Optional[Badge]:
        """Will return the user's favorite badge."""
        if self.private or not(self.badges):
            return None
        Badge: Dict[str, Any] = {'name': '', 'desc': '', 'xp': ''}
        parElem: Optional[BeautifulSoup] = self.soupMain.find(
            'div', class_='favorite_badge')
        if parElem == None:
            return None

        name: str = parElem.find('div', class_='name ellipsis').find(
            'a', class_='whiteLink').text
        for b in self.badges:
            if b.title == name:
                return b
        return None

    def getCounts(self) -> Optional[Dict[str, int]]:
        """Will return the counts of the various items."""
        if self.private:
            return None
        counts: Dict[str, int] = {'badges': 0, 'games': 0, 'screenshots': 0, 'videos': 0, 'workshopitems': 0,
                                  'reviews': 0, 'guides': 0, 'artwork': 0, 'groups': 0, 'friends': 0}
        lblEls: List[BeautifulSoup] = self.soupMain.findAll(
            'span', class_='count_link_label')
        conEls: List[BeautifulSoup] = self.soupMain.findAll(
            'span', class_='profile_count_link_total')
        for i in range(0, len(conEls)):
            key: str = lblEls[i].text.strip().lower()
            if key != 'inventory':
                counts[key] = int(conEls[i].text.strip())
        return counts

    def getBadges(self) -> Optional[List[Badge]]:
        """Will return the earned badges of the user."""
        if self.private:
            return None
        badges: List[Badge] = []
        allElem: List[Any] = self.soupBadges.findAll(
            'div', class_='badge_row_inner')
        for bdinst in allElem:
            badges.append(Badge(bdinst))
        return badges

    def getGames(self) -> Optional[Dict[int, Game]]:
        """Will return the games of the user."""
        if self.private:
            return None
        games: Dict[int, Game] = {}
        rawText: str = RemoveAlls(self.soupGames.findAll('script')[-1].text)
        aftText: str
        try:
            aftText = rawText[rawText.index('[{'):rawText.index('}]')+2]
        except:
            return None
        jsonData = jsld(aftText)

        for i in range(0, len(jsonData)):
            games[jsonData[i]['appid']] = Game(jsonData[i])
        return games

    def getRecents(self) -> Optional[List[Game]]:
        """Will return the recently played games of the user."""
        if self.private or not(self.games):
            return None
        strRecents: List[str] = []
        recents: List[Game] = []
        allGames: List[BeautifulSoup] = self.soupMain.findAll(
            'div', class_='recent_game_content')
        for gameElem in allGames:
            parElem: BeautifulSoup = gameElem.find('div', class_='game_name')
            nameElem: BeautifulSoup = parElem.find('a', class_='whiteLink')
            strRecents.append(nameElem.text.strip())
        for game in self.games:
            if self.games[game].name in strRecents:
                recents.append(self.games[game])
        return recents

    def getWishlist(self) -> Optional[Dict[int, Any]]:
        """Will return the wishlist of the user."""
        if self.private:
            return None
        games: Dict[int, Any] = {}
        allGames = self.soupWish.findAll('div', class_='wishlistRowItem')
        for game in allGames:
            app: int = MakeInt(game.find('div', class_='popup_block2')['id'])
            priceElem: Optional[BeautifulSoup] = game.find('div', class_='discount_final_price') if game.find(
                'div', class_='discount_final_price') != None else game.find('div', class_='price')

            rawPrice: str = '' if priceElem == None else priceElem.text.strip().lower()
            price: float
            if 'free' in rawPrice:
                price = 0
            price = MakeFloat(rawPrice)

            games[app] = {}
            games[app]['name'] = game.find('h4', class_='ellipsis').text
            games[app]['price'] = price
            games[app]['rank'] = MakeInt(
                game.find('div', class_='wishlist_rank_ro').text)
            games[app]['date'] = game.find(
                'div', class_='wishlist_added_on ellipsis').text.strip().replace('Added on ', '')
        return games


if __name__ == '__main__':
    """Handles the script if run from a console."""
    print('Hello Console!')
    evan: User = User(s64='76561198069463927')
    jon: User = User(s64='76561198065605885')
