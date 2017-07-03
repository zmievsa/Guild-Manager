#!/usr/bin/env python3

from lib.errors import ErrorManager, sendErrorMessage
from lib.config import failure_image, succeed_image
from lib.wiki_pages import refreshGuilds

from topics.modules import guild_changes, guild_battles, guild_making, #make_eweek
from topics.lib import Request, getComments


def main():
	topic_list = (guild_changes, guild_battles, guild_making,) #make_eweek
	parseTopics(topic_list)
	refreshGuilds()


def parseTopics(topic_list):
	for topic in topic_list:
		comments = getComments(topic, topic.comment_amount)
		try:
			parseChanges(comments, topic)
		except Exception as e:
			sendErrorMessage("topics", e)


def parseChanges(comments, topic):
	""" Парсинг обсуждения и внесение изменений """
	for comment in comments:
		from_id, text, comment_already_checked = breakUpComment(comment)
		if not comment_already_checked:
			request = Request(text, from_id, comment['id'], topic)
			request.process()
			request.finish()


def breakUpComment(comment):
	""" Возвращает нужные нам поля из комментария """
	from_id = str(comment['from_id'])
	text = comment['text'].strip()
	attachments = comment.get('attachments')
	comment_already_checked = attachments is not None
	return from_id, text, comment_already_checked


if __name__ == "__main__":
	with ErrorManager("topics"):
		main()
