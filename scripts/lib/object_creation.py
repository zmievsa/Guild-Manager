""" Занесение объектов в базу данных """

from lib.config import group_id, my_id, std_avatar_id
from lib.commands import vk, api, database
from lib.wiki_pages import updateGuild
from lib.guilds import Player
from logging import getLogger

logger = getLogger("GM.lib.creation")


class StandardObjectCreation:
	""" Стандартное создание элементов базы данных

		Рекоммендуется использовать дочерние классы исключительно
		через заявки и обсуждения (topics), так как все проверки
		правильности введенных данных не входят в создание объекта.
	"""
	custom_id = False

	def __init__(self, *args, **kwargs):
		logger.debug("{} with args='{}', kwargs={}".format(
			type(self).__name__, args, kwargs))
		args = list(args)
		if not self.custom_id:
			object_id = self.getId()
			args.insert(0, object_id) # Id must come first
		if self.parent:
			self.editArgs(args, kwargs)
			database.addElement(self.parent, args)
		else:
			raise Exception("Parent not found")

	def getId(self, minimal_id="1"):
		all_ids = database.getAll(self.parent, field="id")
		if all_ids:
			return max(all_ids) + 1
		else:
			return minimal_id


class createGuild(StandardObjectCreation):
	parent = "guilds"

	def __init__(self, *args):
		super().__init__(*args)
		self.createGuildPlayers()
		updateGuild(id)

	def editArgs(self, args, kwargs):
		name = args[1]
		args.insert(3, self.getPage(name))
		args.insert(5, 0) # wins
		args.insert(6, 0) # loses

	def getPage(self, name):
		""" У любой гильдии есть вики-страница в ВК """
		page_id = vk(api.pages.save,
					text="",
					title=name,
					user_id=my_id,
					group_id=group_id)
		return page_id

	def createGuildPlayers(self, players, guild_id):
		""" Часто игроков новых гильдий нет в базе данных """
		logger.debug("Creating players of guild {}".format(guild_id))
		for player in players:
			old_player = Player(id=player.id)
			if not old_player.exists:
				createPlayer(id=player.id, name=player.name, guild=guild_id)
			else:
				old_player.set("guild", guild_id)


class createPlayer(StandardObjectCreation):
	parent = "players"
	custom_id = True

	def editArgs(self, args, kwargs):
		guild_id = kwargs.get("guild_id", 0)
		args.insert(2, guild_id)
		args.insert(3, std_avatar_id)


class createEweek(StandardObjectCreation):
	parent = "eweeks"


class createAvatar(StandardObjectCreation):
	parent = "avatars"


class createAchi(StandardObjectCreation):
	parent = "achis"
