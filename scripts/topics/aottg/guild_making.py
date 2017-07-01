from lib.database_objects import createGuild
from lib.guilds import Player, Guild
from lib.commands import ban_list
from lib.config import group_id

from topics.errors import GMError
from topics.lib import Hyperlink
from re import search


id = 29891323
group = group_id
comment_amount = 5


def getAction(text):
	return makeGuild


def getResponse(text, asker):
	player = Player(asker.get("id"))
	guild_name, page_id = player.guild.get("name", "page")
	link = "https://vk.com/page-{}_{}".format(group_id, page_id)
	return "Гильдия: {} ({})".format(guild_name, link)


def makeGuild(request):
	guild = getGuildInfo(request.text)
	checkMissingFields(guild)
	addMissingFields(guild)
	makeHyperlinks(guild)
	editHeadsAndVices(guild)
	if not guildAlreadyExists(guild):
		checkGuildInfo(guild)
		guild = createGuild(**guild)


def getGuildInfo(text):
	text = text.splitlines()
	guild = dict()
	for line in text:
		line_lower = line.lower()
		if ":" not in line:
			continue
		stripped_line = line[line.find(":") + 1:].strip()
		if "баннер" in line_lower or "лого" in line_lower:
			photo_line = stripped_line[stripped_line.find("photo"):]
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


def checkMissingFields(guild):
	mandatory_fields = {
	"head":"Глава",
	"name":"Название",
	"players":"Состав",
	"requirements":"Требования",
	"about":"Описание",
	"banner":"Баннер",
	"logo":"Лого"}
	for field in mandatory_fields:
		if field not in guild:
			field_name = mandatory_fields[field]
			raise GMError("Поле '{}' не найдено.".format(field_name))


def addMissingFields(guild):
	field_list = "vice",
	for field in field_list:
		if field not in guild:
			guild[field] = ""


def makeHyperlinks(guild):
	fields = ("head", "vice", "players")
	for field in fields:
		players = guild[field].strip().split(" ")
		guild[field] = [Hyperlink(p) for p in players]


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
