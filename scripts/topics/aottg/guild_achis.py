from topics.lib import getFields, checkMissingFields
from topics.errors import GMError

from lib.guilds import Player, Guild, Achi
from lib.commands import ban_list
from lib.config import aottg_main


# id = 29901188
group = aottg_main
comment_amount = 15


def getAction(text):
	return main


def getResponse(request):
	return "Гильдия: " + request.asker.guild.get("name")


def main(request):
	keys = "гильдия", "испытание", "участники", "волны"
	fields = getFields(request.text, keys)
	checkMissingFields(fields, keys)
	editFields(fields)
	checkFields(fields)
	addAchiPoints(fields)
	request.asker.guild = fields['гильдия']


def editFields(fields):
	players = fields['участники'].split(" ")
	fields['участники'] = [Player(p) for p in players]
	fields['волны'] = int(fields['волны'])
	fields['гильдия'] = Guild(fields['гильдия'])
	fields['испытание'] = Achi(fields['испытание'])


def checkFields(fields):
	checkGuild(fields['гильдия'])
	checkAchi(fields['испытание'])
	checkWaves(fields['испытание'], fields['волны'])
	checkParticipants(fields['участники'], fields['гильдия'])


def checkGuild(guild):
	if not guild.exists:
		raise GMError("Такой гильдии не существует")


def checkAchi(achi):
	if not achi.exists:
		raise GMError("Такого испытания не существует")


def checkWaves(achi, waves):
	wave_count = len(achi.wave_pics) - 1
	if wave_count < waves:
		raise GMError("Слишком много волн")


def checkParticipants(players, guild):
	guild = guild.get("id")
	for player in players:
		isbanned = "{} забанен в группе".format(player.name)
		not_in_guild = "{} не состоит в гильдии".format(player.name)
		if not player.inguild:
			raise GMError(not_in_guild)
		elif player.get("guild") != guild.get("id"):
			raise GMError(not_in_guild)
		elif int(player.get("id")) in ban_list:
			raise GMError(isbanned)


def addAchiPoints(fields):
	guild_achi = fields['гильдия'].get("achi")
	achi_id = fields['испытание'].get("id")
	waves = fields['волны']
	guild_achi[achi_id] = str(waves)
	fields['гильдия'].set("achi", guild_achi)
