#!/usr/bin/env python3

from lib.errors import ErrorManager, sendErrorMessage
from lib.topics import Request, getComments
from lib.config import topics_folder
from lib.wiki_pages import refreshGuilds

from importlib import import_module
from logging import getLogger
import os

logger = getLogger("GM.check_topics")


def main():
	topics = getTopics(topics_folder)
	parseTopics(topics)
	refreshGuilds()


def getTopics(folder):
	for file in os.listdir(folder):
		name, extension = os.path.splitext(file)
		if extension == ".py" and not name.startswith("ignore"):
			yield import_module("topics.modules." + name)


def parseTopics(topic_list):
	logger.debug("Started parsing topics")
	for topic in topic_list:
		comments = getComments(topic, topic.comment_amount)
		try:
			parseChanges(comments, topic)
		except Exception as e:
			logger.exception("Exception occured in topic '{}'".format(topic.__name__))
			sendErrorMessage("topics", e)


def parseChanges(comments, topic):
	""" Парсинг обсуждения и внесение изменений """
	logger.debug("Parsing '{}' topic...".format(topic.__name__))
	for comment in comments:
		from_id, text, comment_already_checked = breakUpComment(comment)
		if not comment_already_checked:
			request = Request(text, from_id, comment['id'], topic)
			request.process()
			request.finish()


def breakUpComment(comment):
	""" Возвращает нужные нам атрибуты комментария """
	from_id = comment['from_id']
	text = comment['text'].strip()
	attachments = comment.get('attachments')
	comment_already_checked = attachments is not None
	return from_id, text, comment_already_checked


if __name__ == "__main__":
	with ErrorManager("topics"):
		main()
