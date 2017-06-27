from lxml import etree as XML
from lib.guilds import Player
from lib.commands import api, database, group_id, my_id


class StandardObjectCreation:
	def make(self, **kwargs):
		xml_element = makeXMLElement(self.parent)
		kwargs["id"] = self.getId()
		fields = makeFields(self.keys, kwargs)
		enterIntoDatabase(fields, xml_element)

	def getId(self, minimal_id="1"):
		all_ids = database.getAll(self.parent, field="id")
		if all_ids is not None:
			all_ids = (int(i) for i in all_ids)
			new_id = max(all_ids) + 1
			return str(new_id)
		else:
			return minimal_id


class createGuild(StandardObjectCreation):
	parent = "guilds"
	keys = ("id", "name", "page", "head", "vice",
		"wins", "loses", "requirements",
		"about", "logo", "banner")

	def __init__(self, **kw):
		kw['wins'], kw['loses'] = "0", "0"
		kw['page'] = self.getPage(kw['name'])
		self.make(**kw)
		self.createGuildPlayers(kw['players'], kw['id'])

	def getPage(self, name):
		page = api.pages.save(text="", title=name, group_id=group_id, user_id=my_id)
		return str(page)

	def createGuildPlayers(self, players, guild_id):
		for player in players:
			existing_player = Player(id=player.id)
			if existing_player is None:
				createPlayer(id=player.id, name=player.name, guild=guild_id)
			else:
				existing_player.set("guild", guild_id)


class createEweek(StandardObjectCreation):
	"""
		Args:
		str diff = Сложность
		str goal = Цель игры
		str map = Название карты
		str settings = доп. условия
		str ch1, ch2, ch3 = челленджи
	"""
	parent = "eweeks"
	keys = ("id", "map", "diff", "goal",
	"ch1", "ch2", "ch3", "settings")

	def __init__(self, **kwargs):
		self.make(kwargs)


class createAvatar(StandardObjectCreation):
	keys = "id", "link"

	def __init__(self, link):
		self.make(link=link)


def createPlayer(id, name, guild="0"):
	""" Добавляет игрока в базу данных """
	xml_element = makeXMLElement("players")
	std_avatar = "29"
	fields = (
		("id", id), ("name", name),
		("guild", guild), ("avatar", std_avatar))
	enterIntoDatabase(fields, xml_element)


def makeXMLElement(parent_name, element_name=None):
	element_name = element_name or parent_name[:-1]
	parent = database.find(parent_name)
	return XML.SubElement(parent, element_name)


def makeFields(keys, kwargs):
	return [(key, kwargs[key]) for key in keys]


def enterIntoDatabase(fields, xml_element):
	for name, value in fields:
		field = XML.SubElement(xml_element, name)
		field.text = value
