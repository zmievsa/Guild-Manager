""" Набор абстракций над базой данных """

from abc import ABC as AbstractBaseClass, abstractmethod
from logging import getLogger
from enum import IntEnum

from lib.commands import database, vk, api
from lib.config import my_id, group_id
from lib import wiki_pages



logger = getLogger("GM.lib.guilds")


class Rank(IntEnum):
	head = 3
	vice = 2
	player = 1
	not_in_guild = 0


class DatabaseElement(AbstractBaseClass):
	""" Стандартный набор методов работы с объектами """
	
	def __init__(self, **kwargs):
		key, value = getPositiveKwarg(kwargs)
		self.makeAttributes(key, value)

	def set(self, name, value):
		logger.debug("Setting '{}' to {} of {} ({})".format(
			name, value, repr(self), type(self).__name__))
		database.setField(self.parent, self.id, name, value)
		self.__setattr__(name, value)

	def makeAttributes(self, column, value):
		""" Поиск элемента в базе данных """
		response = database.getByField(self.parent, column, value)
		self.exists = bool(response)
		if self.exists:
			for key, value in response.items():
				self.__setattr__(key, value)

	@classmethod
	def create(cls, **kwargs):
		logger.debug("Creating {} object...".format(cls.__name__))
		cls._editKwargs(kwargs)
		special_kwargs = cls._popSpecialKwargs(kwargs)
		element_id = database.addElement(cls.parent, kwargs=kwargs)
		instance = cls.getInstance(kwargs, element_id)
		instance._finishCreation(special_kwargs)
		return instance

	@classmethod
	def _editKwargs(cls, kwargs):
		""" If an object has special fields """

	@classmethod
	def _popSpecialKwargs(cls, kwargs):
		""" If an object recieves some additional information in kwargs and needs to save it until finishCreation"""
		return {}

	def _finishCreation(self, special_kwargs):
		""" If an object needs to do anything else in order to be created """

	@classmethod
	def getInstance(cls, kwargs, object_id):
		""" Override, if an object uses something different from 'id' as a primary key """
		return cls(id=object_id)


class Guild(DatabaseElement):
	parent = "guilds"

	def __init__(self, id=None, name=None):
		super().__init__(id=id, name=name)

	def setPosition(self, player_id, position):
		""" Меняет статус игрока в гильдии

			Возможные аргументы:
			"player", "vice", "head"
		"""
		self._removePlayerFromOldPosition(player_id)
		if position != "player": # player is the absense of position
			self._putPlayerIntoNewPosition(player_id, position)

	@property
	def heads(self):
		return self.head.split(" ")

	@property
	def vices(self):
		if self.vice:
			return self.vice.split(" ")
		else:
			return []

	def _removePlayerFromOldPosition(self, player_id):
		heads, vices = self.heads, self.vices
		if player_id in heads:
			heads.remove(player_id)
			self.set("head", " ".join(heads))
		elif player_id in self.vices:
			vices.remove(player_id)
			self.set("vice", " ".join(vices))

	def _putPlayerIntoNewPosition(self, player_id, position):
		if position == "head":
			initial_value = self.head
		elif position == "vice":
			initial_value = self.vice
		new_value = "{} {}".format(initial_value, player_id)
		self.set(position, new_value)

	@classmethod
	def _editKwargs(cls, kwargs):
		kwargs["wins"] = kwargs["loses"] = 0
		kwargs["page"] = cls._makePage(kwargs["name"])

	@classmethod
	def _popSpecialKwargs(cls, kwargs):
		return {"players":kwargs.pop("players")}

	def _finishCreation(self, special_kwargs):
		self._createPlayers(special_kwargs["players"])
		wiki_pages.updateGuild(self.id)

	@staticmethod
	def _makePage(name):
		""" У любой гильдии есть вики-страница в ВК """
		page_id = vk(api.pages.save,
					text="",
					title=name,
					user_id=my_id,
					group_id=group_id)
		return page_id

	def _createPlayers(self, players):
		""" Часто игроков новых гильдий нет в базе данных """
		logger.debug("Creating players of guild {}".format(self.id))
		for player in players:
			old_player = Player(player.id)
			if not old_player.exists:
				Player.create(id=player.id, name=player.name, guild_id=self.id)
			else:
				old_player.set("guild_id", self.id)


class Player(DatabaseElement):
	parent = "players"
	custom_id = True

	def __init__(self, id=None, name=None):
		self.name = name
		self.id = id
		super().__init__(id=id, name=name)
		self.guild = self.getGuild()
		self.rank = self.getRank()

	def __repr__(self):
		""" Удобно в еженедельниках """
		if self.exists or (self.id and self.name):
			return "[id{}|{}]".format(self.id, self.name)
		elif self.name:
			return self.name
		else:
			return self.id

	@property
	def inguild(self):
		return self.rank > 0

	def getGuild(self):
		if self.exists:
			if self.guild_id != 0:
				return Guild(self.guild_id)

	def getRank(self):
		if self.guild is not None:
			player_id = str(self.id)
			if player_id in self.guild.heads:
				return Rank.head
			elif player_id in self.guild.vices:
				return Rank.vice
			else:
				return Rank.player
		else:
			return Rank.not_in_guild

	def _editKwargs(cls, kwargs):
		if "guild_id" not in kwargs:
			kwargs["guild_id"] = 0
		kwargs["avatar"] = 29


class Eweek(DatabaseElement):
	parent = "eweeks"

	def __init__(self, id):
		super().__init__(id=id)
		if self.exists:
			self.challenges = self.challenges.split(" ")

	def __repr__(self):
		return self.formatRules()

	def formatRules(self):
		""" Генерирует правила еженедельника """
		text = "{} {}, {} ({})"
		if self.goal is None:
			text = text.replace(", ", "")
		if self.settings is None:
			text = text[:9] # cut out the '()'
		return text.format(self.map, self.diff, self.goal, self.settings)


class Achi(DatabaseElement):
	parent = "achis"

	def __init__(self, id):
		super().__init__(id=id)
		self.waves = self.waves.split(" ")

	@staticmethod
	def getEmptyProgressField():
		""" Выводит поле ачей для гильдий

			Используется при создании гильдии
			или при перезапуске ачей, чтобы
			обозначить, что все ачи не пройдены
		"""
		achis = database.getAll("achis") or ''
		progress = ["0"] * len(achis)
		return " ".join(progress)


class Avatar(DatabaseElement):
	parent = "avatars"

	def __init__(self, id=None, link=None):
		super().__init__(id=id, link=link)

	def __repr__(self):
		return self.link


def getPositiveKwarg(kwargs):
	for key, value in kwargs.items():
		if value:
			return key, value
	else:
		return "id", None
