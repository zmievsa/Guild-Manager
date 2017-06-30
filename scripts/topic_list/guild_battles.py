from lib.errors import GB_wrong_request, GB_guild_not_found
from lib.commands import test_id
from lib.guilds import Guild


id = 35465123
group = test_id
comment_amount = 25


def getAction(text):
	return addWinsOrLoses


def getMessage(text, asker):
	return "Гильдия: {}".format(asker.guild.get("name"))


def addWinsOrLoses(request):
	result = getResult(request.text)
	guild = getGuild(request.text, result)
	if result == "поражение":
		xml = guild.find("loses") 
	elif result == "победа":
		xml = guild.find("wins")
	xml.text = str(int(xml.text) + 1)
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
