#!/usr/bin/env python3
"""A Steam API written for python without the clunky Steam API
"""
from requests import get as req
from bs4 import BeautifulSoup as soup
from json import loads as jsld
from re import sub as reg

__author__ = 'Evan Young'
__copyright__ = 'Copyright 2017-2018, Evan Young'
__credits__ = 'Evan Young'

__license__ = 'GNU GPLv3'
__version__ = '1.3.5'
__maintainer__ = 'Evan Young'
__status__ = 'Production'


RemoveAlls = lambda text: reg('[\t\r\n]', '', text)
MakeInt = lambda text: int(reg('[^0-9]', '', text))
MakeFloat = lambda text: float(reg('[^0-9.]', '', text))


class user:
    """Will return a user object, with various information about the user."""

    def __init__(self, s64=None, sid=None):
        """Will return a user object, with various information about the user."""
        if(s64 != None):
            s64 = str(s64)
            if(len(s64) != 17):
                raise Exception('The Steam64 provided is invalid')
            aft = f'profiles/{s64}/'
        elif(sid != None):
            sid = str(sid)
            aft = f'id/{sid}/'
        else:
            raise Exception('Invalid user parameters')

        self.url = f'http://steamcommunity.com/{aft}'
        self.soupMain = soup(req(self.url).text, 'html.parser')
        if('error' in self.soupMain.title.text.lower()):
            raise Exception('Error retrieveing Steam Profile')
        self.soupDate = soup(req(f'{self.url}badges/1/').text, 'html.parser')
        self.soupBadges = soup(req(f'{self.url}badges/').text, 'html.parser')
        self.soupGames = soup(req(f'{self.url}games/?tab=all').text, 'html.parser')
        self.soupWish = soup(req(f'{self.url}wishlist/').text, 'html.parser')
        self.private = self.getPrivate()
        self.persona = self.getPersona()
        self.avatar = self.getAvatar()

        self.name = None if self.private else self.getName()
        self.date = None if self.private else self.getDate()
        self.location = None if self.private else self.getLocation()
        self.status = None if self.private else self.getStatus()
        self.level = None if self.private else self.getLevel()
        self.favBadge = None if self.private else self.getFavBadge()
        self.counts = None if self.private else self.getCounts()
        self.badges = None if self.private else self.getBadges()
        self.games = None if self.private else self.getGames()
        self.recents = None if self.private else self.getRecents()
        self.wishlist = None if self.private else self.getWishlist()
        self.aliases = None if self.private else self.getAliases()

    def printAll(self):
        """For debugging purposes, prints all the non-callable items in the user object."""
        [print(f'{a}: {self.__getattribute__(a)}') for a in dir(self) if not a.startswith('__') and not a.startswith('soup') and not callable(self.__getattribute__(a)) and a != 'req']
        print()

    def getPrivate(self):
        """Will return a bool of whether or not the profile is private."""
        return self.soupMain.find('div', class_='profile_private_info') != None

    def getPersona(self):
        """Will return the display-name (persona) of the user."""
        elem = self.soupMain.find('span', class_='actual_persona_name')
        persona = elem.text
        return persona

    def getAliases(self):
        """Will return the past display-names."""
        als = []
        data = jsld(req(f'{self.url}ajaxaliases/').text)
        for a in data: als.append(a['newname'])
        return als

    def getName(self):
        """Will return the name of the user."""
        parElem = self.soupMain.find('div', class_='header_real_name ellipsis')
        if(parElem == None): return None
        name = parElem.find('bdi').text
        return name if name != '' else None

    def getLocation(self):
        """Will return the location of the user."""
        loc = {'flag': '', 'contents': ''}
        parElem = self.soupMain.find('div', class_='header_real_name ellipsis')
        if(parElem == None or parElem.find('img') == None): return None
        loc['flag'] = parElem.find('img')['src']
        loc['contents'] = parElem.contents[-1].strip()
        return loc

    def getDate(self):
        """Will return the creation-date of the Steam Profile."""
        since = self.soupDate.find('div', class_='badge_description').text
        since = RemoveAlls(since.replace('Member since', ''))
        since = since.replace('Member since', '')
        since = since.replace('.', '')
        return since

    def getAvatar(self):
        """Will return the url of the avatar of the user."""
        elem = self.soupMain.find('div', class_='playerAvatarAutoSizeInner').find('img')
        return elem['src']

    def getStatus(self):
        """Will return the status of the user."""
        status = {'main': ''}
        mainElem = self.soupMain.find('div', class_='profile_in_game_header')
        descElem = self.soupMain.find('div', class_='profile_in_game_name')
        status['main'] = mainElem.text.replace('Currently ', '').lower()
        if(status['main'] == 'offline'):
            status['last'] = descElem.text.replace('Last Online ', '').lower()
        elif(status['main'] == 'in-game'):
            status['game'] = descElem.text
        return status

    def getLevel(self):
        """Will return the Steam level of the user."""
        elem = self.soupMain.find('span', class_='friendPlayerLevelNum')
        level = MakeInt(elem.text)
        return level

    def getFavBadge(self):
        """Will return the user's favorite badge."""
        Badge = {'name': '', 'desc': '', 'xp': ''}
        parElem = self.soupMain.find('div', class_='favorite_badge')
        if(parElem == None): return None

        nameElem = parElem.find('div', class_='name ellipsis').find('a', class_='whiteLink')
        descElem = parElem.find('div', class_='favorite_badge_icon')
        xpElem = parElem.find('div', class_='xp')
        Badge['name'] = nameElem.text
        Badge['desc'] = descElem.attrs['data-tooltip-html'].replace('<br>', '').split('\n')
        Badge['xp'] = MakeInt(xpElem.text)
        return Badge

    def getCounts(self):
        """Will return the counts of the various items."""
        counts = {'badges':0,'games':0,'screenshots':0,'videos':0,'workshopitems':0,'reviews':0,'guides':0,'artwork':0,'groups':0,'friends':0}
        lblEls = self.soupMain.findAll('span', class_='count_link_label')
        conEls = self.soupMain.findAll('span', class_='profile_count_link_total')
        for i in range(0, len(conEls)):
            key = lblEls[i].text.strip().lower()
            if(key != 'inventory'): counts[key] = int(conEls[i].text.strip())
        return counts

    def getBadges(self):
        """Will return the earned badges of the user."""
        badges = []
        allElem = self.soupBadges.findAll('div', class_='badge_row_inner')
        for bdinst in allElem: badges.append(Badge(bdinst))
        return badges

    def getGames(self):
        """Will return the games of the user."""
        games = {}
        rawText = RemoveAlls(self.soupGames.findAll('script')[-1].text)
        aftText = rawText[rawText.index('[{'):rawText.index('}]')+2]
        jsonData = jsld(aftText)

        for i in range(0, len(jsonData)): games[jsonData[i]['appid']] = Game(jsonData[i])
        return games

    def getRecents(self):
        """Will return the recently games of the user."""
        recents = []
        allGames = self.soupMain.findAll('div', class_='recent_game_content')
        for game in allGames:
            parElem = game.find('div', class_='game_name')
            nameElem = parElem.find('a', class_='whiteLink')
            recents.append(nameElem.text.strip())
        return recents

    def getWishlist(self):
        """Will return the wishlist of the user."""
        games = {}
        allGames = self.soupWish.findAll('div', class_='wishlistRowItem')
        for game in allGames:
            app = MakeInt(game.find('div', class_='popup_block2')['id'])
            priceElem = game.find('div', class_='discount_final_price') if (game.find('div', class_='discount_final_price') != None) else game.find('div', class_='price')

            price = '' if priceElem == None else priceElem.text.strip().lower()
            if('free' in price): price = '0'
            if(price != None and price != ''): price = MakeFloat(price)

            games[app] = {}
            games[app]['name'] = game.find('h4', class_='ellipsis').text
            games[app]['price'] = price
            games[app]['rank'] = MakeInt(game.find('div', class_='wishlist_rank_ro').text)
            games[app]['date'] = game.find('div', class_='wishlist_added_on ellipsis').text.strip().replace('Added on ', '')
        return games


class Badge:
    """Will return a badge object, with various information about each badge."""

    def __init__(self, inst):
        """Will return a badge object, with various information about each badge."""
        self.inst = inst
        self.title = self.getTitle()
        self.game = self.getGame()
        self.xp = self.getLevXP()[0]
        self.level = self.getLevXP()[1]
        self.date = self.getDate()

    def getTitle(self):
        """Will return the title of the card."""
        title = self.inst.find('div', class_='badge_info_title').text
        return title

    def getGame(self):
        """Will return the game (or source) of the card."""
        game = self.inst.find('div', class_='badge_title').text.split('\xa0')[0].strip()
        return game

    def getLevXP(self):
        """Will return the level and/or the xp of the card."""
        lvlxp = RemoveAlls(self.inst.find('div', class_='').text).split(',')
        for i in range(0, len(lvlxp)): lvlxp[i] = MakeInt(lvlxp[i])

        lvlxp.reverse()
        lvlxp.append(None)
        return lvlxp

    def getDate(self):
        """Will return the date the user earned the badge."""
        date = self.inst.find('div', class_='badge_info_unlocked').text.strip().replace('Unlocked ', '')
        return date


class Game:
    """Will return a game object, with various information about each game."""

    def __init__(self, inst):
        """Will return a game object, with various information about each game."""
        self.appid = inst['appid']
        self.name = inst['name']
        self.logo = inst['logo']
        self.hours = MakeFloat(inst['hours_forever']) if 'hours_forever' in inst else 0
        self.recent = MakeFloat(inst['hours']) if 'hours' in inst else 0
        self.last = inst['last_played'] if 'last_played' in inst else 0


if __name__ == '__main__':
    """Handles the script if run from a console."""
    print('Hello Console!')
    evan = user(s64='76561198069463927')
    #evan.printAll()


def test_main():
    """Runs the testing."""
    evan = user(s64='76561198069463927')
    evay = user(sid='BritishMystery')
    assert type(evan) != None
    assert evan.level != None
    assert len(evan.games) > 0
    assert evan.games[105600].hours != 0
    assert evan.games[105600].hours != ''
