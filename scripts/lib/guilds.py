""" Набор абстракций над базой данных """

from lib.commands import database, vk, api
from lib.config import my_id, group_id
from logging import getLogger
from lib import wiki_pages
from enum import IntEnum


logger = getLogger("GM.lib.guilds")


class Rank(IntEnum):
	head = 3
	vice = 2
	player = 1
	not_in_guild = 0


class DatabaseElement:
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
		logger.debug("Making attributes of {}, '{}'={} ({})".format(
			type(self).__name__, column, value, type(value).__name__))
		response = database.getByField(self.parent, column, value)
		self.exists = bool(response)
		if self.exists:
			for key, value in response.items():
				self.__setattr__(key, value)

	def create(self, **kwargs):
		logger.debug("Creating {} object...".format(self.__name__))
		self._editKwargs(kwargs)
		database.addElement(self.parent, **kwargs)
		self._finishCreation(self, kwargs)

	def _editKwargs(self, kwargs):
		""" Если у объекта есть стандартные или необычные поля """

	def _finishCreation(self, kwargs):
		""" Если объекту для создания нужно сделать еще что-либо """


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

	def _editKwargs(self, kwargs):
		self.players = kwargs.pop("players")
		kwargs["wins"] = kwargs["loses"] = 0
		kwargs["page"] = self._makePage(kwargs["name"])

	def _finishCreation(self, kwargs):
		self.__init__(name=kwargs["name"])
		self._createPlayers()
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

	def _createPlayers(self):
		""" Часто игроков новых гильдий нет в базе данных """
		logger.debug("Creating players of guild {}".format(self.id))
		for player in self.players:
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

	def _editKwargs(self, kwargs):
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
