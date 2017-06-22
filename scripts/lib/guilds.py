from lib.commands import database, api, group_id, my_id
import lxml.etree as XML


class DatabaseElement(object):
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
		if id is not None:
			self._checkid(id)
			return database.getById(self.parent, id)
		elif name is not None:
			return database.getByField(self.parent, "name", name)
		else:
			raise Exception("DatabaseElement: ты не указал id или имя")

	@staticmethod
	def _checkid(id):
		if type(id) is not str and type(id) is not int:
			raise Exception("ID error: value:{}, type:{}".format(id, type(id)))


class Eweek(DatabaseElement):
	parent = "eweeks"

	def __init__(self, id):
		self.xml_element = self.getElement(id)


class Avatar(DatabaseElement):
	parent = "avatars"

	def __init__(self, id):
		self.xml_element = self.getElement(id)

	def __repr__(self):
		return self.get("link")


class Player(DatabaseElement):
	parent = "players"

	def __init__(self, id=None, name=None):
		self.xml_element = self.getElement(id, name)
		self.guild = self.getGuild()
		self.rank = self.getRank()
		self.name = name
		self.id = id

	def __repr__(self):
		if self.exists or (self.id and self.name):
			if self.exists:
				id, name = self.get("id", "name")
			else:
				id, name = self.id, self.name
			return "[id{}|{}]".format(id, name)
		elif self.name:
			return self.name

	@property
	def inguild(self):
		return self.rank > 0

	def recreate(self, id, name):
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
		if not field:
			return []
		else:
			return field.split(" ")

	def setPosition(self, player_id, position):
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


def createGuild(players, name, head, vice, requirements, about, logo, banner):
	""" Добавляет гильдию в базу данных """
	guild_id = getGuildId()
	page = makeGuildPage(name)
	xml_element = makeGuildXMLElement()
	fields = (
		("id", guild_id), ("name", name),
		("page", page),   ("head", head),
		("vice", vice),   ("wins", "0"),
		("loses", "0"),   ("requirements", requirements),
		("about", about), ("logo", logo),
		("banner", banner))
	enterIntoDatabase(fields, xml_element)
	createGuildPlayers(players, guild_id)
	database.rewrite()


def getGuildId():
	first_guild_id = "1"
	guild_ids = database.getAll(kind="guilds", field="id")
	if guild_ids is not None:
		guild_ids = (int(id) for id in guild_ids)
		new_id = max(guild_ids) + 1
		return str(new_id)
	else:
		return first_guild_id


def createGuildPlayers(players, guild_id):
	for player in players:
		existing_player = Player(id=player.id)
		if existing_player is None:
			createPlayer(id=player.id, name=player.name, guild=guild_id)
		else:
			existing_player.set("guild", guild_id)


def makeGuildPage(name):
	page = api.pages.save(text="", title=name, group_id=group_id, user_id=my_id)
	return str(page)


def makeGuildXMLElement():
	guilds = database.find("guilds")
	new_guild = XML.SubElement(guilds, "guild")
	return new_guild


def createPlayer(id, name, guild="0"):
	""" Добавляет игрока в базу данных """
	xml_element = makePlayerXMLElement()
	std_avatar = "29"
	fields = (
		("id", id), ("name", name),
		("guild", guild), ("avatar", std_avatar))
	enterIntoDatabase(fields, xml_element)


def makePlayerXMLElement():
	players = database.find("players")
	xml_element = XML.SubElement(players, "player")
	return xml_element


def enterIntoDatabase(fields, xml_element):
	for name, value in fields:
		field = XML.SubElement(xml_element, name)
		field.text = value
