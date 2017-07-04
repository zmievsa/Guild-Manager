""" Создание объектов и занесение их в базу данных """

from lib.commands import vk, api, database
from lib.config import group_id, my_id
from lib.guilds import Player, Achi
from lxml.etree import SubElement


class StandardObjectCreation:
	""" Стандартное создание элементов базы данных

		Оно включает в себя обязательный id и создание полей
		с помощью словаря kwargs, где ключи -- названия полей.
		Выстраиваются они в последовательности, заданной в
		keys атрибуте дочернего класса. Элемент создается
		в контейнере parent (Players, Guilds, etc).

		Рекоммендуется использовать дочерние классы исключительно
		через заявки и обсуждения (topics), так как все проверки
		правильности введенных данных не входят в создание объекта.
	"""
	def make(self, **kwargs):
		xml_element = makeXMLElement(self.parent)
		kwargs["id"] = self.getId()
		fields = self.makeFields(kwargs)
		enterIntoDatabase(fields, xml_element)

	def getId(self, minimal_id="1"):
		all_ids = database.getAll(self.parent, field="id")
		if all_ids is not None:
			all_ids = (int(i) for i in all_ids)
			new_id = max(all_ids) + 1
			return str(new_id)
		else:
			return minimal_id

	def makeFields(self, kwargs):
		""" Позволяет сделать неслучайный порядок полей """
		return [(key, kwargs[key]) for key in self.keys]


class createGuild(StandardObjectCreation):
	parent = "guilds"
	keys = ("id", "name", "page", "head", "vice",
		"wins", "loses", "requirements", "about",
		"logo", "banner", "achi")

	def __init__(self, **kw):
		kw['achi'] = Achi.getEmptyField()
		kw['wins'], kw['loses'] = "0", "0"
		kw['page'] = self.getPage(kw['name'])
		self.make(**kw)
		self.createGuildPlayers(kw['players'], kw['id'])

	def getPage(self, name):
		""" У любой гильдии есть вики-страница в ВК """
		page = vk(api.pages.save,
					text="",
					title=name,
					user_id=my_id,
					group_id=group_id)
		return str(page)

	def createGuildPlayers(self, players, guild_id):
		""" Часто игроков новых гильдий нет в базе данных """
		for player in players:
			old_player = Player(id=player.id)
			if not old_player.exists:
				createPlayer(id=player.id, name=player.name, guild=guild_id)
			else:
				old_player.set("guild", guild_id)


class createEweek(StandardObjectCreation):
	parent = "eweeks"
	keys = ("id", "map", "diff", "goal",
	"challenges", "settings")

	def __init__(self, **kwargs):
		self.make(**kwargs)


class createAvatar(StandardObjectCreation):
	keys = "id", "link"

	def __init__(self, link):
		self.make(link=link)


class createAchi(StandardObjectCreation):
	keys = "id", "name", "icon", "waves"

	def __init__(self, **kwargs):
		self.make(**kwargs)


def createPlayer(id, name, guild="0"):
	"""Использование функции обусловлено нестандартным id """
	xml_element = makeXMLElement("players")
	std_avatar = "29"
	fields = (
		("id", id), ("name", name),
		("guild", guild), ("avatar", std_avatar))
	enterIntoDatabase(fields, xml_element)
	return Player(id)


def makeXMLElement(parent_name, element_name=None):
	""" Чаще всего объект в контейнере имеет то же название (guilds: guild) """
	element_name = element_name or parent_name[:-1]
	parent = database.find(parent_name)
	return SubElement(parent, element_name)


def enterIntoDatabase(fields, xml_element):
	for name, value in fields:
		field = SubElement(xml_element, name)
		field.text = value
