#!/usr/bin/env python3

from lib.wiki_pages import updateGuild
from lib.errors import ErrorManager
from lib.commands import database


def updateAllGuilds():
	guild_ids = database.getAll(parent="guilds", field="id")
	for guild_id in guild_ids:
		updateGuild(guild_id)


if __name__ == "__main__":
	with ErrorManager("UpdateGuilds"):
		updateAllGuilds()