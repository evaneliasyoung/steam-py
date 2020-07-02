#!/usr/bin/env python3
"""A Steam API written for python without the clunky Steam API
"""
from json import loads as jsld
from datetime import datetime as dt
from re import sub as reg
from typing import List, Dict, Optional, Any
from os import system
from bs4 import BeautifulSoup
from requests import get as req

__author__ = 'Evan Elias Young'
__copyright__ = 'Copyright 2017-2020, Evan Elias Young'
__credits__ = 'Evan Elias Young'

__license__ = 'GNU GPLv3'
__version__ = '1.4.0'
__maintainer__ = 'Evan Elias Young'
__status__ = 'Production'


def remove_all_ws(text: str) -> str:
    """Will remove all tabs, returns, and newlines from text."""
    return reg('[\t\r\n]', '', text)


def make_int(text: str) -> int:
    """Will make the first sequence of digits an integer."""
    return int(reg('[^0-9]', '', text))


def make_float(text: str) -> float:
    """Will make the first sequence of digits a float."""
    return float(reg('[^0-9.]', '', text))


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
        self.title: str = self.get_title()
        self.game: str = self.get_game()
        self.exp: int = self.get_exp()
        self.level: Optional[int] = self.get_level()
        self.earned: int = self.get_earn_time()

    def get_title(self) -> str:
        """Will return the title of the card."""
        return str(self.inst.find('div', class_='badge_info_title').text)

    def get_game(self) -> str:
        """Will return the game (or source) of the card."""
        return str(self.inst.find('div', class_='badge_title').text.split('\xa0')[0].strip())

    def get_level(self) -> Optional[int]:
        """Will return the level of the card."""
        lvlxp: List[str] = remove_all_ws(
            self.inst.find('div', class_='').text).split(',')
        if len(lvlxp) == 2:
            return make_int(lvlxp[0])
        return None

    def get_exp(self) -> int:
        """Will return the experience of the card."""
        lvlxp: List[str] = remove_all_ws(
            self.inst.find('div', class_='').text).split(',')
        if len(lvlxp) == 2:
            return make_int(lvlxp[1])
        return make_int(lvlxp[0])

    def get_earn_time(self) -> int:
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
        self.hours: float = make_float(
            inst['hours_forever']) if 'hours_forever' in inst else 0.0
        self.recent: float = make_float(
            inst['hours']) if 'hours' in inst else 0.0
        self.last: int = int(inst['last_played']) * \
            1000 if 'last_played' in inst else 0


class User:
    """Will return a user object, with various information about the user."""

    def __init__(self, s64: Optional[str] = None, sid: Optional[str] = None) -> None:
        """Will return a user object, with various information about the user."""
        if s64 is not None:
            if len(str(s64)) != 17:
                raise Exception('The Steam64 provided is invalid')
            aft = f'profiles/{str(s64)}/'
        elif sid is not None:
            aft = f'id/{str(sid)}/'
        else:
            raise Exception('Invalid user parameters')

        self.url: str = f'http://steamcommunity.com/{aft}'
        self.soup_main = BeautifulSoup(req(self.url).text, 'html.parser')
        if 'error' in self.soup_main.title.text.lower():
            raise Exception('Error retrieveing Steam Profile')
        self.soup_date = BeautifulSoup(
            req(f'{self.url}badges/1/').text, 'html.parser')
        self.soup_badges = BeautifulSoup(
            req(f'{self.url}badges/').text, 'html.parser')
        self.soup_games = BeautifulSoup(
            req(f'{self.url}games/?tab=all').text, 'html.parser')
        self.soup_wish = BeautifulSoup(
            req(f'{self.url}wishlist/').text, 'html.parser')
        self.private: bool = self.get_private()
        self.persona: str = self.get_persona()
        self.avatar: str = self.get_avatar()

        self.name: Optional[str] = self.get_name()
        self.created: Optional[int] = self.get_creation_time()
        self.location: Optional[Location] = self.get_location()
        self.status: Optional[Status] = self.get_status()
        self.level: Optional[int] = self.get_level()
        self.counts: Optional[Dict[str, int]] = self.get_counts()
        self.badges: Optional[List[Badge]] = self.get_badges()
        self.favorite_badge: Optional[Badge] = self.get_favorite_badge()
        self.games: Optional[Dict[int, Game]] = self.get_games()
        self.recents: Optional[List[Game]] = self.get_recents()
        self.wishlist: Optional[Dict[int, Any]] = self.get_wishlist()
        self.aliases: Optional[List[str]] = self.get_aliases()

    def print_all(self) -> None:
        """For debugging purposes, prints all the non-callable items in the user object."""
        for key in dir(self):
            if not key.startswith('__') and not key.startswith('soup') and not callable(self.__getattribute__(key)) and key != 'req':
                print(f'{key}: {self.__getattribute__(key)}')
        print()

    def get_private(self) -> bool:
        """Will return a bool of whether or not the profile is private."""
        return bool(self.soup_main.find('div', class_='profile_private_info') is not None)

    def get_persona(self) -> str:
        """Will return the display-name (persona) of the user."""
        return str(self.soup_main.find('span', class_='actual_persona_name').text)

    def get_aliases(self) -> Optional[List[str]]:
        """Will return the past display-names."""
        if self.private:
            return None
        aliases: List[str] = []
        data: List[Dict[str, str]] = jsld(req(f'{self.url}ajaxaliases/').text)
        for alias in data:
            aliases.append(alias['newname'])
        return aliases

    def get_name(self) -> Optional[str]:
        """Will return the name of the user."""
        if self.private:
            return None
        par_el: Optional[BeautifulSoup] = self.soup_main.find(
            'div', class_='header_real_name ellipsis')
        if par_el is None or par_el.find('bdi').text == '':
            return None
        return par_el.find('bdi').text

    def get_location(self) -> Optional[Location]:
        """Will return the location of the user."""
        if self.private:
            return None
        par_el: Optional[BeautifulSoup] = self.soup_main.find(
            'div', class_='header_real_name ellipsis')
        if par_el is None or par_el.find('img') is None:
            return None
        return Location(par_el.find('img')['src'], par_el.contents[-1].strip())

    def get_creation_time(self) -> Optional[int]:
        """Will return the creation-time of the Steam Profile."""
        if self.private:
            return None
        year: int = int(remove_all_ws(self.soup_date.find(
            'div', class_='badge_description').text)[-5: -1])
        tmp: List[str] = remove_all_ws(self.soup_date.find(
            'div', class_='badge_info_unlocked').text)[9:].split(' ')
        return int(dt.strptime(f'{year} {tmp[0]} {tmp[1][:2]:0>2} {tmp[-1].upper():0>7}', '%Y %b %d %I:%M%p').timestamp() * 1000)

    def get_avatar(self) -> str:
        """Will return the url of the avatar of the user."""
        return str(self.soup_main.find('div', class_='playerAvatarAutoSizeInner').find('img')['src'])

    def get_status(self) -> Optional[Status]:
        """Will return the status of the user."""
        if self.private:
            return None
        main_el: BeautifulSoup = self.soup_main.find(
            'div', class_='profile_in_game_header')
        desc_el: BeautifulSoup = self.soup_main.find(
            'div', class_='profile_in_game_name')
        main: str = main_el.text.replace('Currently ', '').lower()
        last: Optional[str] = None
        game: Optional[str] = None
        if desc_el:
            if main == 'offline':
                last = desc_el.text.replace('Last Online ', '').lower()
            elif main == 'in-game':
                game = desc_el.text
        return Status(main, game, last)

    def get_level(self) -> int:
        """Will return the Steam level of the user."""
        if self.private:
            return False
        elem: BeautifulSoup = self.soup_main.find('span', class_='friendPlayerLevelNum')
        level: int = make_int(elem.text)
        return level

    def get_favorite_badge(self) -> Optional[Badge]:
        """Will return the user's favorite badge."""
        if self.private or not self.badges:
            return None
        par_el: Optional[BeautifulSoup] = self.soup_main.find(
            'div', class_='favorite_badge')
        if par_el is None:
            return None

        name: str = par_el.find('div', class_='name ellipsis').find(
            'a', class_='whiteLink').text
        for badge in self.badges:
            if badge.title == name:
                return badge
        return None

    def get_counts(self) -> Optional[Dict[str, int]]:
        """Will return the counts of the various items."""
        if self.private:
            return None
        counts: Dict[str, int] = {'badges': 0, 'games': 0, 'screenshots': 0, 'videos': 0, 'workshopitems': 0,
                                  'reviews': 0, 'guides': 0, 'artwork': 0, 'groups': 0, 'friends': 0}
        lbl_els: List[BeautifulSoup] = self.soup_main.findAll(
            'span', class_='count_link_label')
        cnt_els: List[BeautifulSoup] = self.soup_main.findAll(
            'span', class_='profile_count_link_total')
        for i, cnt_el in enumerate(cnt_els):
            key: str = lbl_els[i].text.strip().lower()
            if key != 'inventory':
                counts[key] = int(cnt_el.text.strip())
        return counts

    def get_badges(self) -> Optional[List[Badge]]:
        """Will return the earned badges of the user."""
        if self.private:
            return None
        badges: List[Badge] = []
        all_el: List[Any] = self.soup_badges.findAll(
            'div', class_='badge_row_inner')
        for bd_el in all_el:
            badges.append(Badge(bd_el))
        return badges

    def get_games(self) -> Optional[Dict[int, Game]]:
        """Will return the games of the user."""
        if self.private:
            return None
        games: Dict[int, Game] = {}
        raw_text: str = remove_all_ws(self.soup_games.findAll('script')[-1].text)
        aft_text: str
        try:
            aft_text = raw_text[raw_text.index('[{'):raw_text.index('}]')+2]
        except:
            return None
        json_data = jsld(aft_text)

        for game, _i in enumerate(json_data):
            games[game['appid']] = Game(game)
        return games

    def get_recents(self) -> Optional[List[Game]]:
        """Will return the recently played games of the user."""
        if self.private or not self.games:
            return None
        str_recents: List[str] = []
        recents: List[Game] = []
        all_games: List[BeautifulSoup] = self.soup_main.findAll(
            'div', class_='recent_game_content')
        for game_el in all_games:
            par_el: BeautifulSoup = game_el.find('div', class_='game_name')
            name_el: BeautifulSoup = par_el.find('a', class_='whiteLink')
            str_recents.append(name_el.text.strip())
        for game in self.games:
            if self.games[game].name in str_recents:
                recents.append(self.games[game])
        return recents

    def get_wishlist(self) -> Optional[Dict[int, Any]]:
        """Will return the wishlist of the user."""
        if self.private:
            return None
        games: Dict[int, Any] = {}
        all_games = self.soup_wish.findAll('div', class_='wishlistRowItem')
        for game in all_games:
            app: int = make_int(game.find('div', class_='popup_block2')['id'])
            price_el: Optional[BeautifulSoup] = game.find('div', class_='discount_final_price') if game.find(
                'div', class_='discount_final_price') is not None else game.find('div', class_='price')

            str_price: str = '' if price_el is None else price_el.text.strip().lower()
            price: float
            if 'free' in str_price:
                price = 0
            price = make_float(str_price)

            games[app] = {}
            games[app]['name'] = game.find('h4', class_='ellipsis').text
            games[app]['price'] = price
            games[app]['rank'] = make_int(
                game.find('div', class_='wishlist_rank_ro').text)
            games[app]['date'] = game.find(
                'div', class_='wishlist_added_on ellipsis').text.strip().replace('Added on ', '')
        return games


if __name__ == '__main__':
    print('Hello Console!')
    evan: User = User(s64='76561198069463927')
    evan.print_all()
    jon: User = User(s64='76561198065605885')
    jon.print_all()
