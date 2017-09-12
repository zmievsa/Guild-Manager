#!/usr/bin/env python3

from lib.errors import ErrorManager
from lib.commands import database
from lib.achi import getAchiField
from lib.guilds import Guild


def main():
	enableAchiConfig()
	resetAchiProgress()
	database.rewrite()


def enableAchiConfig():
	file_name = "lib/config.py"
	old_line = "achi_is_active = False"
	new_line = "achi_is_active = True"
	text = getConfig(file_name)
	new_text = text.replace(old_line, new_line)
	editConfig(file_name, new_text)


def getConfig(file_name):
	with open(file_name, "r") as config:
		return config.read()


def editConfig(file_name, new_text):
	with open(file_name, "w") as config:
		config.write(new_text)


def resetAchiProgress():
	guilds = getGuilds()
	achi_field = getAchiField()
	for guild in guilds:
		guild.set("achi", achi_field)


def getGuilds():
	guild_ids = database.getAll("guilds", "id")
	return [Guild(id=id) for id in guild_ids]


if __name__ == "__main__":
	with ErrorManager("start_achi"):
		main()
