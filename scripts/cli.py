#!/usr/bin/env python3

from argparse import ArgumentParser
from logging import getLogger

from lib.commands import database
from lib.guilds import Guild
from lib.guilds import Player
from lib.wiki_pages import refreshGuilds
from lib.wiki_pages import updateGuild
from topics.modules.guild_changes import endGuild
from topics.modules.guild_changes import excludeFromGuild

import backup_database
import check_topics
import eweek_notify
import make_eweek_post
import make_weekly_posts
import update_guilds

logger = getLogger("GM.command_line")


scripts = {
	"backupdata":backup_database.backup,
	"mkweekly":make_weekly_posts.generate,
	"mkeweek":make_eweek_post.make,
	"updguilds":update_guilds.main,
	"chtopics":check_topics.main,
	"notify":eweek_notify.notify,
}


def main():
	parser = makeParser()
	request = parser.parse_args()
	handleRequest(request)


def makeParser():
	main_parser = ArgumentParser("Guild Manager")
	script_help = "[{}]".format(", ".join(list(scripts.keys())))
	main_parser.add_argument("-s", "--script", dest="scripts",
		nargs="+", choices=scripts.keys(), metavar="", help=script_help)
	makeGuildParser(main_parser)
	return main_parser


def makeGuildParser(main_parser):
	main_subparsers = main_parser.add_subparsers()
	guilds = main_subparsers.add_parser("guilds")
	guilds_subparsers = guilds.add_subparsers(dest="guild_command")
	exclude = guilds_subparsers.add_parser("exclude")
	exclude.add_argument("id")
	setrank = guilds_subparsers.add_parser("setrank")
	setrank.add_argument("id")
	setrank.add_argument("rank", choices=["player", "vice", "head"])
	endguild = guilds_subparsers.add_parser("endguild")
	endguild.add_argument("id")


def handleRequest(request):
	if request.scripts is not None:
		for script in request.scripts:
			scripts[script]()
			logger.debug("Script '{}' finished".format(script))
	elif "guild_command" in request:
		handleGuildCommand(request)


def handleGuildCommand(request):
	command = request.guild_command
	if command == "exclude":
		player = Player(request.id)
		guild = player.guild
		excludeFromGuild(player)
	elif command == "setrank":
		guild = player.guild
		guild.setPosition(request.id, request.rank)
	elif command == "endguild":
		guild = Guild(request.id)
		endGuild(guild)
		refreshGuilds()
	database.rewrite()
	updateGuild(guild.id)


main()
