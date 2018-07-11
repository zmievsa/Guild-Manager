""" Испытания """

from topics.errors import GMError
from lib.topics import Fields

from lib.guilds import Player, Guild, Achi
from lib.commands import ban_list
from lib.config import group_id


# id = 29901188 	# TODO
group = group_id
comment_amount = 83


def getAction(text):
	return main


def getResponse(request):
	return "Гильдия: " + request.asker.guild.name


def finish(request):
	pass


def main(request):
	mandatory_keys = "гильдия", "испытание", "участники", "волны"
	fields = Fields(request.text, mandatory_keys)
	editFields(fields)
	checkFields(fields)
	addAchiPoints(fields)
	request.guilds_to_update.append(fields['гильдия'])


def editFields(fields):
	players = fields['участники'].split(" ")
	fields['участники'] = [Player(id=p) for p in players]
	fields['волны'] = int(fields['волны'])
	fields['гильдия'] = Guild(name=fields['гильдия'])
	fields['испытание'] = Achi(name=fields['испытание'])


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
	guild = guild.id
	for player in players:
		isbanned = "{} забанен в группе".format(player.name)
		not_in_guild = "{} не состоит в гильдии".format(player.name)
		if not player.inguild:
			raise GMError(not_in_guild) # FIX, WHERE DID U GET THESE?
		elif player.guild != guild.id:
			raise GMError(not_in_guild) # FIX, WHERE DID U GET THESE?
		elif player.id in ban_list:
			raise GMError(isbanned)		# FIX, WHERE DID U GET THESE?


def addAchiPoints(fields):
	# should be buggy AF
	guild_all_achi = fields['гильдия'].achi
	achi_id = fields['испытание'].id
	waves = fields['волны']
	guild_all_achi[achi_id] = str(waves)
	fields['гильдия'].set("achi", guild_all_achi)
