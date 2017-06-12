#!/usr/bin/env python3
from lib.commands import api, database, group_id, error
from lib.guilds import createGuild
from re import search


def makeGuild():
	comment = getTopicComment()
	text = comment['text'].splitlines()
	guild = getGuildInfo(text)
	checkPlayers(guild['players'])
	guild = addMissingFields(guild)
	guild = createGuild(**guild)


def getTopicComment():
	guild_topic = 29891323
	offset = api.board.getComments(
		group_id=group_id,
		topic_id=guild_topic,
		count=1)['count']
	offset -= 1
	comment = api.board.getComments(
		group_id=group_id,
		topic_id=guild_topic,
		offset=offset,
		count=1)['items'][0]
	return comment


def getGuildInfo(text):
	guild = dict()
	for line in text:
		line_lower = line.lower()
		stripped_line = line[line.index(":") + 1:].strip()
		if "баннер" in line_lower or "лого" in line_lower:
			photo_line = stripped_line[stripped_line.index("photo"):]
		if "название:" in line_lower:
			guild['name'] = stripped_line
		elif "глава:" in line_lower:
			guild['head'] = stripped_line
		elif "зам:" in line_lower:
			guild['vice'] = stripped_line
		elif "состав:" in line_lower:
			guild['players'] = stripped_line
		elif "требования:" in line_lower:
			guild['requirements'] = stripped_line
		elif "описание:" in line_lower:
			guild['about'] = stripped_line
		elif "баннер:" in line_lower:
			guild['banner'] = photo_line
		elif "лого:" in line_lower:
			guild['logo'] = photo_line
	return guild


def checkPlayers(players):
	players = players.split(" ")
	for player in players:
		id_, name = splitHyperlink(player)
		checkHyperlinkFormat(player)
		checkNameUniqueness(id_, name)
		checkIfPlayerHasGuild(id_, name)


def splitHyperlink(player):
	player = player[3:-1]
	id_, name = player.split("|")
	return id_, name


def checkHyperlinkFormat(player):
	if search(r"^\[id\d+\|[A-Za-z_\d]+\]$", player) is None:
		raise Exception(player + " неправильно оформлен.")


def checkNameUniqueness(id_, name):
	old_player = database.getByField(kind="players", field="name", value=name)
	if old_player is not None:
		if old_player.find("id").text != id_:
			raise Exception("Игрок с ником " + name + " уже существует.")


def checkIfPlayerHasGuild(id_, name):
	player = database.getById(kind="players", id=id_)
	if player is not None:
		guild_id = player.find("guild").text
		if guild_id != "0":
			guild = database.getById("guilds", guild_id)
			guild_name = guild.find("name").text
			raise Exception(name + " уже состоит в гильдии " + guild_name)


def addMissingFields(guild):
	field_list = (
		"name", "head", "vice", "players",
		"requirements", "about", "banner", "logo")
	for field in field_list:
		if field not in guild:
			guild[field] = ""
	return guild


if __name__ == "__main__":
	try:
		makeGuild()
	except:
		error("makeGuild")
