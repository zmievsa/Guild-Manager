""" Набор абстракций над базой данных """

from lib.commands import database
from logging import getLogger
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
		column, value = tuple(kwargs.items())[0]
		self.makeAttributes(column, value)

	def set(self, name, value):
		logger.debug("Setting '{}' to {} of {} ({})".format(
			name, value, repr(self), type(self).__name__))
		database.setField(self.parent, self.id, name, value)
		self.__setattr__(name, value)

	def makeAttributes(self, column, value):
		""" Поиск элемента в базе данных """
		logger.debug("Making attributes of {}, '{}'={} ({})".format(
			type(self).__name__, column, value, type(value).__name__))
		values, keys = database.getByField(self.parent, column, value)
		self.exists = bool(values)
		values = values or [None] * len(keys)
		for key, value in zip(keys, values):
			self.__setattr__(key, value)


class Guild(DatabaseElement):
	parent = "guilds"

	@property
	def heads(self):
		return self._getNonEmptyField(self.head)

	@property
	def vices(self):
		return self._getNonEmptyField(self.vice)

	@staticmethod
	def _getNonEmptyField(field):
		""" Почти пустое поле могло бы некорректно отобразиться """
		if field:
			return field.split(" ")
		else:
			return []

	def setPosition(self, player_id, position):
		""" Меняет статус игрока в гильдии

			Возможные аргументы:
			"player", "vice", "head"
		"""
		self._removePlayerFromOldPosition(player_id)
		if position != "player":
			self._putPlayerIntoNewPosition(player_id, position)

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


class Player(DatabaseElement):
	parent = "players"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.guild = self.getGuild()
		self.rank = self.getRank()
		if not self.exists:
			self.name = kwargs.get("name")
			self.id = kwargs.get("id")

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
				return Guild(id=self.guild_id)

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


class Eweek(DatabaseElement):
	parent = "eweeks"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
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

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
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

	def __repr__(self):
		return self.link
