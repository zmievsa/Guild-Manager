from topics.errors import GB_wrong_request, GB_guild_not_found
from lib.wiki_pages import updateGuild
from lib.config import test_id
from lib.guilds import Guild


id = 35465123
group = test_id
comment_amount = 83


def getAction(text):
	return addWinsOrLoses


def getResponse(request):
	return "Гильдия: {}".format(request.asker.guild.get("name"))


def finish(request):
	updateGuild(request.guild_to_update.get("id"))


def addWinsOrLoses(request):
	result = getResult(request.text)
	guild = getGuild(request.text, result)
	addPoints(guild, result)
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
	guild = Guild(name=name)
	if guild.exists:
		return guild
	else:
		raise GB_guild_not_found


def addPoints(guild, result):
	if result == "поражение":
		xml = guild.find("loses")
	elif result == "победа":
		xml = guild.find("wins")
	xml.text = str(int(xml.text) + 1)
