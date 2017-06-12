#!/usr/bin/env python3

from topic_list import guild_changes, guild_battles
from lib.topics import Request, failure_image, succeed_image, getComments
from lib.wiki_pages import refreshGuilds
from lib.commands import error


def main():
	lst = (guild_changes, guild_battles)
	for topic in lst:
		comments = getComments(topic, 20)
		parseChanges(comments, topic)
	refreshGuilds()


def parseChanges(comments, topic):
	""" Парсинг обсуждения и внесение изменений """
	for comment in comments:
		from_id, string, comment_already_checked = breakUpComment(comment)
		if not comment_already_checked:
			request = Request(string, from_id, comment['id'], topic)
			request.process()
			request.finish()


def breakUpComment(comment):
	""" Возвращает нужные нам поля из комментария """
	from_id = str(comment['from_id'])
	string = comment['text'].strip()
	attachments = comment.get('attachments')
	comment_already_checked = commentWasAlreadyChecked(attachments)
	return from_id, string, comment_already_checked


def commentWasAlreadyChecked(attachments):
	""" Проверяет, нужно ли обрабатывать комментарий

		Если к комментарию прикреплено фото "Сделано"
		или "Неправильная заявка" -- комментарий уже
		был проверен. На это и происходит проверка

		returns bool
	"""
	succeed, failure = succeed_image, failure_image
	if attachments is not None:
		for attachment in attachments:
			if attachment.get('photo'):
				a_id = attachment['photo']['id']
			if a_id == failure.id or a_id == succeed.id:
				return True
	return False


if __name__ == "__main__":
	try:
		main()
	except:
		error("topics")
