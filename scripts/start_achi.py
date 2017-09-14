#!/usr/bin/env python3

from lib.errors import ErrorManager
from lib.commands import database
from lib.achi import getAchiField
from lib.guilds import Guild


ACHI_FIELD_ID = 1


def main():
	resetAchiProgress()
	enableAchi()
	database.save()


def enableAchi():
	database.setField("config", ACHI_FIELD_ID, field="value", value=1)


def resetAchiProgress():
	guilds = getGuilds()
	achi_field = getAchiField()
	for guild in guilds:
		guild.set("achi_progress", achi_field)


def getGuilds():
	guild_ids = database.getAll("guilds", "id")
	return [Guild(id=id) for id in guild_ids]


if __name__ == "__main__":
	with ErrorManager("start_achi"):
		main()
