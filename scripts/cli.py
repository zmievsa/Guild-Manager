#!/usr/bin/env python3

from argparse import ArgumentParser

from topics.modules.guild_changes import endGuild, excludeFromGuild
from lib.guilds import Player, Guild
from lib.commands import database

import backup_database
import make_weekly_posts
import make_eweek_post
import update_guilds
import check_topics
import eweek_notify


scripts = {
	"backupdata":backup_database.backup,
	"mkweekly":make_weekly_posts.generate, 
	"mkeweek":make_eweek_post.make,
	"updguilds":update_guilds.updateAllGuilds,
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
			print("Script '{}' finished".format(script))
	elif "guild_command" in request:
		if request.command == "exclude":
			player = Player(request.id)
			excludeFromGuild(player)
			print(player.get("name"), "excluded.")
		elif request.command == "setrank":
			player.guild.setPosition(request.id, request.rank)
		elif request.command == "endguild":
			endGuild(Guild(request.id))
		database.rewrite()
	else:
		print(request)


main()
