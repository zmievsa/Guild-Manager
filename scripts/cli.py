#!/usr/bin/env python3

from argparse import ArgumentParser
import backup_database, make_weekly_posts, make_eweek_post, update_guilds, check_topics, eweek_notify


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
	request = parser.parse_args([])
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
	elif hasattr(request, "command"):
		if request.command == "exclude":
			excludeFromGuild(request.id)
		elif request.command == "setrank":
			Player(request.id).guild.setRank(request.rank)
		elif request.command == "endguild":
			endGuild(request.id)


main()
