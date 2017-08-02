#!/usr/bin/env python3
"""A Steam API written for python without the clunky Steam API
"""
from requests import get as req
from bs4 import BeautifulSoup
from json import loads
from re import sub as reg
from math import floor

__author__ = "Evan Young"
__copyright__ = "Copyright 2017, Evan Young"
__credits__ = "Evan Young"

__license__ = "GNU GPLv3"
__version__ = "1.1.1"
__maintainer__ = "Evan Young"
__status__ = "Development"


RemoveTags = lambda text: reg('<[^>]*>', '', text)
RemoveTabs = lambda text: text.replace('\t', '')
RemoveRets = lambda text: text.replace('\r', '')
RemoveNews = lambda text: text.replace('\n', '')
RemoveAlls = lambda text: RemoveTabs(RemoveRets(RemoveNews(text)))
MakeInt = lambda text: int(reg('[^0-9]', '', text))
MakeFloat = lambda text: float(reg('[^0-9.]', '', text))
class user:
   def __init__(self, steam64):
      """Returns a user object, with various information about the user

      steam64: The Steam64ID of the user
      """

      steam64 = str(steam64)
      if(len(steam64) != 17): raise Exception("The Steam64 provided is invalid")

      self.url = f'http://steamcommunity.com/profiles/{steam64}/'
      self.soupMain = BeautifulSoup(req(self.url).text, 'html.parser')
      self.soupBadges = BeautifulSoup(req(f'{self.url}badges/').text, 'html.parser')
      self.soupGames = BeautifulSoup(req(f'{self.url}games/?tab=all').text, 'html.parser')
      self.soupWish = BeautifulSoup(req(f'{self.url}wishlist/').text, 'html.parser')
      self.private = self.getPrivate()
      self.persona = self.getPersona()
      if(self.private):
         self.name = None
         self.avatar = None
         self.status = None
         self.level = None
         self.favBadge = None
         self.counts = None
         self.badges = None
         self.games = None
         self.wishlist = None
      else:
         self.name = self.getName()
         self.avatar = self.getAvatar()
         self.status = self.getStatus()
         self.level = self.getLevel()
         self.favBadge = self.getFavBadge()
         self.counts = self.getCounts()
         self.badges = self.getBadges()
         self.games = self.getGames()
         self.wishlist = self.getWishlist()
   def printAll(self):
      """For debugging purposes, prints all the non-callable items in the user object
      """
      
      [print(f'{a}: {self.__getattribute__(a)}') for a in dir(self) if not a.startswith('__') and not a.startswith('soup') and not callable(evan.__getattribute__(a)) and a != 'req']
      print()
   def getPrivate(self):
      """Returns a bool of whether or not the profile is private
      """

      return self.soupMain.find('div', class_='profile_private_info') != None
   def getPersona(self):
      """Returns the display-name (persona) of the user
      """

      elem = self.soupMain.find('span', class_='actual_persona_name')
      persona = elem.text
      return persona
   def getName(self):
      """Returns the name of the user
      """

      parElem = self.soupMain.find('div', class_='header_real_name ellipsis')
      name = parElem.find('bdi').text
      return name if name != '' else None
   def getAvatar(self):
      """Returns the url of the avatar of the user
      """

      elem = self.soupMain.find('div', class_='playerAvatarAutoSizeInner').find('img')
      return elem['src']
   def getStatus(self):
      """Returns the status of the user
      """
      
      status = {'main': ''}
      mainElem = self.soupMain.find('div', class_='profile_in_game_header')
      descElem = self.soupMain.find('div', class_='profile_in_game_name')
      status['main'] = mainElem.text.replace('Currently ', '').lower()
      if(status['main'] == "offline"):
         status['last'] = descElem.text.replace('Last Online ', '').lower()
      elif(status['main'] == "in-game"):
         status['game'] = descElem.text
      return status
   def getLevel(self):
      """Returns the Steam level of the user
      """
      
      elem = self.soupMain.find('span', class_='friendPlayerLevelNum')
      level = MakeInt(elem.text)
      return level
   def getFavBadge(self):
      """Returns the user's favorite badge
      """
      
      Badge = {'name': '', 'desc': '', 'xp': ''}
      parElem = self.soupMain.find('div', class_='favorite_badge')
      if(parElem == None): return None
      
      nameElem = parElem.find('div', class_='name ellipsis').find('a', class_='whiteLink')
      descElem = parElem.find('div', class_='favorite_badge_icon')
      xpElem = parElem.find('div', class_='xp')
      Badge['name'] = nameElem.text
      Badge['desc'] = descElem.attrs['data-community-tooltip'].replace('<br>', '').split('\n')
      Badge['xp'] = MakeInt(xpElem.text)
      return Badge
   def getCounts(self):
      """Returns the counts of the various items
      """

      counts = {'badges':0,'games':0,'screenshots':0,'videos':0,'workshopitems':0,'reviews':0,'guides':0,'artwork':0,'groups':0,'friends':0}
      lblEls = self.soupMain.findAll('span', class_='count_link_label')
      conEls = self.soupMain.findAll('span', class_='profile_count_link_total')
      for i in range(0, len(conEls)):
         key = lblEls[i].text.strip().lower()
         if(key != 'inventory'): counts[key] = int(conEls[i].text.strip())
      return counts
   def getBadges(self):
      """Returns the earned badges of the user
      """

      badges = []
      allElem = self.soupBadges.findAll('div', class_='badge_row_inner')
      for bdinst in allElem: badges.append(Badge(bdinst))
      return badges
   def getGames(self):
      """Returns the games of the user
      """

      games = {}
      rawText = RemoveAlls(self.soupGames.findAll('script')[-1].text)
      aftText = rawText[rawText.index('[{'):rawText.index('}]')+2]
      jsonData = loads(aftText)
      for i in range(0, len(jsonData)): games[jsonData[i]['appid']] = Game(jsonData[i])
      return games
   def getWishlist(self):
      """Returns the wishlist of the user
      """

      games = {}
      allGames = self.soupWish.findAll('div', class_='wishlistRowItem')
      for game in allGames:
         app = MakeInt(game.find('div', class_='popup_block2')['id'])
         price = game.find('div', class_='price').text.strip().replace('Free to Play', '$0.00')
         games[app] = {}
         games[app]['name'] = game.find('h4', class_='ellipsis').text
         games[app]['price'] = None if price == '' else MakeFloat(price)
         games[app]['rank'] = MakeInt(game.find('div', class_='wishlist_rank_ro').text)
         games[app]['date'] = game.find('div', class_='wishlist_added_on ellipsis').text.strip().replace('Added on ', '')
      return games

class Badge:
   def __init__(self, inst):
      self.inst = inst
      self.title = self.getTitle()
      self.game = self.getGame()
      self.xp = self.getLevXP()[0]
      self.level = self.getLevXP()[1]
      self.date = self.getDate()
   def getTitle(self):
      """Returns the title of the card
      """

      title = self.inst.find('div', class_='badge_info_title').text
      return title
   def getGame(self):
      """Returns the game (or source) of the card
      """
   
      game = self.inst.find('div', class_='badge_title').text.split('\xa0')[0].strip()
      return game
   def getLevXP(self):
      """Returns the level and/or the xp of the card
      """

      lvlxp = RemoveAlls(self.inst.find('div', class_='').text).split(',')      
      for i in range(0, len(lvlxp)): lvlxp[i] = MakeInt(lvlxp[i])
      lvlxp.reverse()
      lvlxp.append(None)
      return lvlxp
   def getDate(self):
      """Returns the date the user earned the badge
      """

      date = self.inst.find('div', class_='badge_info_unlocked').text.strip().replace('Unlocked ', '')
      return date

class Game:
   def __init__(self, inst):
      self.appid = inst['appid']
      self.name = inst['name']
      self.logo = inst['logo']
      self.hours = float(inst['hours_forever']) if 'hours_forever' in inst else 0
      self.recent = float(inst['hours']) if 'hours' in inst else 0         
      self.last = inst['last_played'] if 'last_played' in inst else 0


if __name__ == '__main__':
   print("Hello Console!")
   evan = user('76561198069463927')
   #evan.printAll()
