#!/usr/bin/env python3

from lib.wiki_pages import updateGuild, refreshGuilds
from lib.errors import ErrorManager
from lib.commands import database
from logging import getLogger

logger = getLogger("GM.update_guilds")


def updateAllGuilds():
	logger.debug("Updating all guilds...")
	guild_ids = database.getAll("guilds", field="id")
	for guild_id in guild_ids:
		updateGuild(guild_id)
	refreshGuilds()


if __name__ == "__main__":
	with ErrorManager("UpdateGuilds"):
		updateAllGuilds()
