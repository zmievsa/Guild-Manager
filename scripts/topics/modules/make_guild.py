""" Создание гильдий """

from lib.object_creation import createGuild
from lib.guilds import Player, Guild
from lib.commands import ban_list
from lib.config import group_id

from topics.lib import Hyperlink, getPhoto, Fields
from topics.errors import GMError
from re import search


id = 29891323
group = group_id
comment_amount = 5


def getAction(text):
	return makeGuild


def getResponse(request):
	player = Player(request.asker.id)
	guild_name, page_id = player.guild.get("name", "page")
	link = "https://vk.com/page-{}_{}".format(group_id, page_id)
	return "Гильдия: {} ({})".format(guild_name, link)


def finish(request):
	pass


def makeGuild(request):
	mandatory_keys, optional_keys = getKeys()
	fields = Fields(request.text, mandatory_keys, optional_keys)
	editFields(fields)
	makeHyperlinks(fields)
	editHeadsAndVices(fields)
	if not guildAlreadyExists(fields):
		checkGuildInfo(fields)
		createGuild(**fields)


def getKeys():
	mandatory_keys = {
		"баннер":"banner", "название":"name", "глава":"head",
		"состав":"players", "требования":"requirements",
		"описание":"about", "баннер":"banner", "лого":"logo"}
	optional_keys = {"зам":"vice",}
	return mandatory_keys, optional_keys


def editFields(fields):
	fields['banner'] = getPhoto(fields['banner'])
	fields['logo'] = getPhoto(fields['logo'])


def makeHyperlinks(guild):
	fields = ("head", "vice", "players")
	for field in fields:
		players = guild[field]
		players = players.strip().split(" ")
		guild[field] = [Hyperlink(p) for p in players if p]


def editHeadsAndVices(guild):
	fields = ("head", "vice")
	for field in fields:
		players = guild[field]
		players = [p.id for p in players]
		guild[field] = " ".join(players)


def checkGuildInfo(guild):
	checkPlayers(guild['players'])
	checkGuildName(guild['name'])
	checkIfHeadsVicesInGuild(guild)


def checkPlayers(players):
	checkNumberOfPlayers(players)
	for player in players:
		checkPlayerUniqueness(player)
		checkIfPlayerHasGuild(player)
		checkIfPlayerInBan(player)


def checkNumberOfPlayers(players):
	if len(players) < 5:
		raise GMError("В гильдии меньше 5 игроков.")


def checkPlayerUniqueness(player):
	old_player = Player(name=player.name)
	if old_player.exists and old_player.get("id") != player.id:
		name = player.name
		id = old_player.get("id")
		raise GMError("Игрок с ником {} уже [id{}|существует]".format(name, id))


def checkIfPlayerHasGuild(hyperlink):
	player = Player(hyperlink.id)
	if player.rank > 0:
		guild_name = player.guild.get("name")
		raise GMError("{} уже состоит в гильдии {}".format(hyperlink, guild_name))


def checkIfPlayerInBan(player):
	if int(player.id) in ban_list:
		raise GMError("{} забанен в группе.".format(player))


def checkGuildName(guild_name):
	pattern = r"^[\[\]A-Za-z_\d ]+$"
	if search(pattern, guild_name) is None:
		raise GMError("Название гильдии содержит недопустимые символы.")
	elif Guild(name=guild_name).exists:
		raise GMError("Гильдия с таким названием уже существует.")


def checkIfHeadsVicesInGuild(guild):
	heads = guild['head'].split(" ")
	vices = guild['vice'].split(" ")
	for player in guild['players']:
		if player.id in heads:
			heads.remove(player.id)
		elif player.id in vices:
			vices.remove(player.id)
	if len(heads) or len(vices):
		raise GMError("Не все заместители/главы находятся в составе гильдии.")


def guildAlreadyExists(guild):
	name = guild['name']
	head = guild['head']
	old_guild = Guild(name=name)
	if old_guild.exists:
		if old_guild.get("head") == head:
			return True
