""" Набор абстракций над базой данных """

from lib.commands import database


class DatabaseElement(object):
	""" Стандартный набор методов работы с объектами """
	def find(self, name):
		return self.xml_element.find(name)

	def get(self, *names):
		names = [self.find(n).text or "" for n in names]
		return names if len(names) > 1 else names[0]

	def set(self, name, value):
		self.find(name).text = value

	@property
	def exists(self):
		return self.xml_element is not None

	def getElement(self, id=None, name=None):
		""" Поиск элемента в базе данных """
		if id is not None:
			self._checkid(id)
			return database.getById(self.parent, id)
		elif name is not None:
			return database.getByName(self.parent, name)
		else:
			raise Exception("DatabaseElement: ты не указал id или имя")

	@staticmethod
	def _checkid(id):
		if str is not type(id) is not int:
			raise Exception("Неверный ID: Значение: {}, Тип: {}".format(id, type(id)))


class Guild(DatabaseElement):
	parent = "guilds"

	def __init__(self, id=None, name=None):
		self.xml_element = self.getElement(id, name)

	@property
	def heads(self):
		head = self.get("head")
		return self._getNonEmptyField(head)

	@property
	def vices(self):
		vice = self.get("vice")
		return self._getNonEmptyField(vice)

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
		player_id = str(player_id)
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
			element = self.find("head")
		elif position == "vice":
			element = self.find("head")
		element.text = "{} {}".format(element.text, player_id)


class Player(DatabaseElement):
	parent = "players"

	def __init__(self, id=None, name=None):
		self.xml_element = self.getElement(id, name)
		self.guild = self.getGuild()
		self.rank = self.getRank()
		self.name = name
		self.id = id

	def __repr__(self):
		""" Удобно в еженедельниках """
		if self.exists or (self.id and self.name):
			if self.exists:
				id, name = self.get("id", "name")
			else:
				id, name = self.id, self.name
			return "[id{}|{}]".format(id, name)
		elif self.name:
			return self.name
		else:
			return self.id

	@property
	def inguild(self):
		return self.rank > 0

	def recreate(self, id, name):
		""" Костыль для еженедельника """
		self.__init__(id, name)

	def getGuild(self):
		if self.exists:
			guild_id = self.get("guild")
			if guild_id != "0":
				return Guild(guild_id)

	def getRank(self):
		if self.guild is not None:
			id = self.get("id")
			if id in self.guild.heads:
				return 3
			elif id in self.guild.vices:
				return 2
			else:
				return 1
		else:
			return 0


class Eweek(DatabaseElement):
	parent = "eweeks"

	def __init__(self, id):
		self.xml_element = self.getElement(id)

	def __repr__(self):
		return self.formatRules()

	@property
	def challenges(self):
		return self.get("challenges").split(" ")

	def formatRules(self):
		""" Генерирует правила еженедельника """
		map_, diff, goal, settings = self.get(
			"map", "diff", "goal", "settings")
		text = "{} {}, {} ({})"
		if not goal:
			text = text.replace(", ", "")
		if not settings:
			text = text.replace(" (", "")
			text = text.replace(")", "")
		return text.format(map_, diff, goal, settings)


class Achi(DatabaseElement):
	parent = "achis"

	def __init__(self, id=None, name=None):
		self.xml_element = self.getElement(id, name)

	@property
	def waves(self):
		return self.get("waves").split(" ")

	@staticmethod
	def getEmptyField():
		""" Выводит поле ачей для гильдий

			Используется при создании гильдии
			или при перезапуске ачей, чтобы
			обозначить, что все ачи не пройдены
		"""
		quantity = len(database.getAll("achis"))
		progress = ["0"] * quantity
		return " ".join(progress)


class Avatar(DatabaseElement):
	parent = "avatars"

	def __init__(self, id):
		self.xml_element = self.getElement(id)

	def __repr__(self):
		return self.get("link")
