""" Инструменты для работы с вики-страницами

	Обновление страниц осуществляется в четыре шага:
		Получение шаблона вики-страницы
		Получение атрибутов
		Внесение атрибутов в шаблон
		Сохранение вики-страницы
"""

from lib.commands import database, api, vk, achi_is_active
from lib.config import group_id, my_id, data_folder
from lib import guilds as guildlib

from abc import ABC as AbstractBaseClass
from logging import getLogger

logger = getLogger("GM.lib.wiki_pages")


class NoInstanceObject(AbstractBaseClass):
	def __init__(*args, **kwargs): pass
	def __new__(cls, *args, **kwargs): super().__new__(cls)


class updateGuild(NoInstanceObject):
	""" Обновляет вики-страницу гильдии """
	def __init__(self, guild_id):
		self.guild = guildlib.Guild(id=guild_id)
		if self.guild.exists:
			logger.debug("Updating guild '{}'...".format(self.guild.name))
			self.preparePage()
			self.saveNewPage()
			logger.debug("Finished updating.".format(self.guild.name))

	def preparePage(self):
		self.template = getPageTemplate("guild.txt")
		self.attributes = self.makeAttributes()
		self.page = editPageTemplate(self.attributes, self.template)

	def saveNewPage(self):
		page_id = self.guild.page
		saveWikiPage(self.page, page_id)

	def makeAttributes(self):
		attr = self.getAttributes()
		players = self.getPlayers()
		attr['head'] = self.getHead()
		attr['vice'] = self.getVice()
		attr['stats'] = self.getStats()
		attr['players'] = self.getPlayerList(players)
		attr['numberofplayers'] = len(players)
		if achi_is_active:
			attr['achi'] = self.getAchi()
		else:
			self.template = self.template.replace("[achi]", "")
		return attr

	def getAttributes(self):
		return database.getByField("guilds", "id", self.guild.id)

	def getPlayers(self):
		all_players = database.getAll("players")
		guild_players = []
		for player_id, name, guild_id, avatar in all_players:
			if guild_id == self.guild.id:
				guild_players.append(guildlib.Player(id=player_id))
		return guild_players

	def getHead(self):
		return self.makeFancyList(self.guild.heads)

	def getVice(self):
		vices = self.guild.vices
		if len(vices):
			return self.makeFancyList(vices)
		else:
			self.removeViceField()

	def removeViceField(self):
		template = self.template.splitlines()
		template.pop(6)
		self.template = "\n".join(template)

	def makeFancyList(self, ids):
		""" Список замов или глав """
		players = [guildlib.Player(id=p) for p in ids]
		formatted_list = []
		for player in players:
			hyperlink = "[[id{}|{}]]".format(player.id, player.name)
			formatted_list.append(hyperlink)
		return ", ".join(formatted_list)

	def getStats(self):
		""" Получение процента побед """
		wins = self.guild.wins
		loses = self.guild.loses
		if wins > 0:
			stats = (wins * 100) / (wins + loses)
		else:
			stats = 0
		return round(stats)

	def getPlayerList(self, players):
		""" Составляет список игроков для вики-страницы

			Можно просто забить. Лично я не хочу разбираться
			в том, как это работает. Сорян.
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
			string = "! <center>[[id{}|{}]]</center>\n".format(player.id, player.name)
			player_list += string
			avatar = guildlib.Avatar(id=player.avatar)
			photo = "| [[{}|125x125px;noborder;nolink| ]]\n".format(avatar)
			avatars.append(photo)
			if index == len(players) - 1:
				player_list += new_row
				for a in avatars:
					player_list += a
		return player_list

	def getAchi(self):
		""" Создает отображение списка ачей """
		guild_achi_keys = self.guild.achi.split(" ")
		page = "<br><center>'''[[page-64867627_49895049|Испытания]]'''</center>"
		for index, result in enumerate(guild_achi_keys):
			achi = guildlib.Achi(id=index)
			wave = achi.waves[result]
			title_line = "\n=={}==".format(achi.name)
			icon_pic = "[[{}|125px;noborder| ]]".format(achi.icon)
			wave_pic = "[[{}|400x70px;noborder;nolink| ]]".format(wave)
			main_line = "\n{}{}".format(icon_pic, wave_pic)
			page += title_line + main_line
		return page


class refreshGuilds(NoInstanceObject):
	""" Обновляет страницу гильдий """
	def __init__(self):
		page_id = 47292063
		logger.debug("Refreshing guilds...")
		self.preparePage()
		saveWikiPage(self.page, page_id)
		logger.debug("Finished refreshing")

	def preparePage(self):
		self.template = getPageTemplate("all_guilds.txt")
		self.attributes = self.makeAttributes()
		self.page = editPageTemplate(self.attributes, self.template)

	def makeAttributes(self):
		attr = {}
		attr['all_guilds'], count = self.getGuildList()
		attr['guildnumber'] = count
		attr['playernumber'] = self.getPlayerCount()
		return attr

	def getGuildList(self):
		logger.debug("Getting guild list...")
		guilds = database.getAll("guilds", "id")
		guilds = [guildlib.Guild(id=g) for g in guilds]
		return self.makeFancyGuildList(guilds), len(guilds)

	def makeFancyGuildList(self, guilds):
		""" Создает список гильдий """
		logger.debug("Making fancy guild list...")
		page, id_line, guild_line = self.getGuildLineTemplates()
		total_waves = self.getTotalAmountOfWaves()
		self.makeGuildPercentages(guilds, total_waves)
		self.sortGuilds(guilds)
		for guild in guilds:
			page += id_line.format(guild.percent)
			page += guild_line.format(guild.banner, guild.page)
		page += "\n|}"
		return page

	def getGuildLineTemplates(self):
		""" Базовые шаблоны, которыми наполняется список гильдий """
		if achi_is_active:
			page = "{|\n|-\n!<center>Рейтинг</center>\n!<center>Гильдия</center>\n|-"
			id_line = "\n!<center>{}%</center>"
		else:
			page = "{|\n|-\n!<center>ID</center>\n!<center>Гильдия</center>\n|-"
			id_line = "\n!<center>{}</center>"
		guild_line = "\n|<center>[[{}|450px;noborder|page-64867627_{}]]</center>\n|-"
		return page, id_line, guild_line

	def getTotalAmountOfWaves(self):
		""" Получение всех волн всех ачей для подсчета прохождения """
		if achi_is_active:
			all_achi_waves = database.getAll("achis", "waves")
			all_achi_waves = [len(w.split(" ")) - 1 for w in all_achi_waves]
			return sum(all_achi_waves)

	def makeGuildPercentages(self, guilds, total_waves):
		""" Проценты прохождения ачей """
		for guild in guilds:
			if achi_is_active:
				achi_results = guild.achi.split(" ")
				achi_results = [int(r) for r in achi_results]
				complete_waves = sum(achi_results)
				percent = complete_waves / total_waves
				guild.percent = round(percent)
			else:
				guild.percent = guild.id

	def sortGuilds(self, guilds):
		""" Если ачи -- то наибольший рейтинг сверху
			Если нет ачей -- наименьший ID сверху """
		reverse = achi_is_active
		guilds.sort(key=lambda g: g.percent, reverse=reverse)

	def getPlayerCount(self):
		""" Возвращает только игроков с гильдией """
		player_guilds = database.getAll("players", field="guild_id")
		player_guilds = [g for g in player_guilds if g != 0]
		return len(player_guilds)


def getPageTemplate(file_name):
	path = data_folder + "page_templates/" + file_name
	with open(path, encoding="UTF-8") as file:
		return file.read()


def editPageTemplate(attributes, template):
	""" Заменяет поля в шаблоне значениями атрибутов """
	for key, value in attributes.items():
		key = "[{}]".format(key)
		value = str(value)
		template = template.replace(key, value)
	return template


def saveWikiPage(page, page_id, group=group_id):
	logger.debug("Saving a wiki_page ({})".format(page_id))
	vk(api.pages.save,
		suspend_time=1,
		text=page,
		user_id=my_id,
		page_id=page_id,
		group_id=group)
