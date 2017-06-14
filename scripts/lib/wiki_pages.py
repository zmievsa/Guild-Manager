from lib.commands import database, group_id, my_id, api, vkCap


def updateGuild(guild):
	""" Сформировывает текст для вики-страницы гильдии и сохраняет его в вк
		Args: XML guild

	"""
	with open("../../Data/page_templates/guild.txt", "r") as file:
		template = file.read()
	players = getPlayers(guild)
	guild_children = guild.iterchildren()
	guild_page = guild.find("page")
	attributes = {e.tag:e.text for e in guild_children}
	attributes['numberofplayers'] = str(len(players))
	attributes['stats'] = getStats(attributes['wins'], attributes['loses'])
	attributes['head'] = splitHeadsVices(attributes['head'])
	if attributes['vice'] is not None:
		attributes['vice'] = splitHeadsVices(attributes['vice'])
	else:
		attributes.pop('vice')
		template = template.splitlines()
		template.pop(6)
		template = "\n".join(template)
	attributes['players'] = getPlayerList(players)
	for key in attributes:
		value = attributes[key]
		template = template.replace("[{}]".format(key), value)
	vkCap(api.pages.save, user_id=my_id, text=template, page_id=guild_page, group_id=group_id)


def splitHeadsVices(string):
	""" Возвращает список глав/замов в вики-формате """
	lst = string.split(" ")
	for index, player_id in enumerate(lst):
		player = database.getById(kind="players", id=player_id)
		id = player.find("id").text
		name = player.find("name").text
		lst[index] = "[[id{}|{}]]".format(id, name)
	return ", ".join(lst)


def getStats(wins, loses, precision=False):
	""" Возвращает процент побед гильдии

		Args:
			str wins - количество побед
			str loses - количество поражений
		returns str

	"""
	wins = int(wins)
	loses = int(loses)
	if wins > 0:
		stats = (wins * 100) / (wins + loses)
	else:
		stats = 0
	if precision:
		return stats
	else:
		return str(round(stats))


def getPlayers(guild):
	""" Возвращает список игроков в гильдии

		Args: XML guild
		returns str[][]

	"""
	guild_id = guild.find('id').text
	players = database.find("players").iterchildren()
	guild_players = []
	for player in players:
		if player.find("guild").text == guild_id:
			guild_players.append(player)
	for index, player in enumerate(guild_players):
		player_id = player.find("id").text
		name = player.find("name").text
		avatar_id = player.find("avatar").text
		avatar_element = database.getById(kind="avatars", id=avatar_id)
		avatar = avatar_element.find("link").text
		guild_players[index] = (player_id, name, avatar)
	return guild_players


def getPlayerList(players):
	""" Составляет список игроков для вики-страницы

		Args: XML[] players
		returns str

	"""
	player_list = "{|\n|-\n"
	new_row = "|-\n"
	avatars = []
	for index, player in enumerate(players):
		if len(avatars) == 4:
			player_list += new_row
			for a in avatars:
				player_list += a
			player_list += new_row
			avatars = []
		id, name, avatar = player
		string = "! <center>[[id{}|{}]]</center>\n".format(id, name)
		player_list += string
		photo = "| [[{}|125x125px;noborder;nolink| ]]\n".format(avatar)
		avatars.append(photo)
		if index == len(players) - 1:
			player_list += new_row
			for a in avatars:
				player_list += a
	return player_list


def refreshGuilds():
	""" Обновляет страницу всех гильдий """
	with open("../../Data/page_templates/all_guilds.txt") as file:
		template = file.read()
	all_guilds = list(database.find("guilds").iterchildren())
	attributes = {}
	attributes['all_guilds'] = getGuildList(all_guilds)
	attributes['guildnumber'] = len(all_guilds)
	attributes['playernumber'] = getAllPlayers()
	for key in attributes:
		value = attributes[key]
		template = template.replace("[{}]".format(key), str(value))
	vkCap(api.pages.save, user_id=my_id, text=template, group_id=group_id, page_id=47292063)


def getGuildList(all_guilds):
	""" Возвращает список гильдий для вики-страницы

		Args: XML[] all_guilds
		returns str

	"""
	guild_list = ""
	for guild in all_guilds:
		banner = guild.find('banner').text
		page = guild.find('page').text
		guild_list += "\n<center>[[{}|450px;noborder|page-64867627_{}]]</center>\n".format(banner, page)
	return guild_list


def getAllPlayers():
	""" Возвращает количество игроков во всех гильдиях
		returns int

	"""
	all_players = database.find("players").iterchildren()
	counter = 0
	for player in all_players:
		if player.find("guild").text != "0":
			counter += 1
	return counter
