from lib.commands import database, test_id
from lib.errors import GB_wrong_request, GB_guild_not_found


id = 35465123
group = test_id
comment_amount = 20


def getAction(text):
	return addWinsOrLoses


def getMessage(text, asker):
	return "Гильдия: {}".format(asker.guild.get("name"))


def addWinsOrLoses(request):
	result = getResult(request.text)
	guild = getGuild(request.text, result)
	if result == "поражение":
		guild.loses = guild.loses + 1
	elif result == "победа":
		guild.wins = guild.wins + 1
	request.asker.guild = guild


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
	guild = database.getByField("guilds", "name", name)
	if guild is not None:
		return guild
	else:
		raise GB_guild_not_found
