""" Гильдбои """

from topics.errors import GB_wrong_request, GB_guild_not_found
from lib.config import test_id
from lib.guilds import Guild


id = 35465123
group = test_id
comment_amount = 83


def getAction(text):
	return main


def getResponse(request):
	return "Гильдия: {}".format(request.asker.guild.name)


def finish(request):
	pass


def main(request):
	result = getResult(request.text)
	guild = getGuild(request.text, result)
	addPoints(guild, result)
	request.guilds_to_update.append(guild)


def getResult(text):
	if "победа" in text:
		return "победа"
	elif "поражение" in text:
		return "поражение"
	else:
		raise GB_wrong_request


def getGuild(text, result):
	result_index = text.index(result)
	name = text[:result_index].strip()
	guild = Guild(name=name)
	if guild.exists:
		return guild
	else:
		raise GB_guild_not_found


def addPoints(guild, result):
	if result == "поражение":
		guild.set("loses", guild.loses + 1)
	elif result == "победа":
		guild.set("wins", guild.wins + 1)
