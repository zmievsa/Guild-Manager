from lib.commands import database, api, group_id, my_id
from lib.wiki_pages import updateGuild, refreshGuilds
import lxml.etree as XML


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
	updateGuild(database.getById("guilds", guild_id))
	refreshGuilds()


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
		existing_player = database.getById(kind="players", id=str(id))
		if existing_player is None:
			createPlayer(id=player.id, name=player.name, guild=guild_id)
		else:
			existing_player.find("guild").text = guild_id


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
