#!/usr/bin/env python3

from lib.commands import vk, api, ban_list
from lib.errors import ErrorManager
from lib.config import group_id
from logging import getLogger

logger = getLogger("GM.notify")


def notify():
	""" Оповещает игроков о начале еженедельника """
	message = getMessage()
	logger.debug("Getting eweek players...")
	users = getEweekPlayers()
	users = {user for user in users if user not in ban_list}
	logger.debug("Sending messages...")
	sendMessages(users, message)


def getMessage():
	message = "Еженедельник начался, а ты как раз записался. Приходи, если ещё не сдал!\n"
	warning = "\n(Это автоматическое сообщение. Отвечать на него не нужно.)"
	message += warning
	return message


def getEweekPlayers():
	""" Получение id записавшихся """
	post_id = getEweekPostId()
	comments = getPostComments(post_id)
	users = {comment['from_id'] for comment in comments}
	return users


def getEweekPostId():
	post = vk(api.wall.search, owner_id=-group_id, query="#aottg83_reg", count=1)
	return post['items'][0]['id']


def getPostComments(post_id):
	comments = vk(api.wall.getComments, owner_id=-group_id, post_id=post_id, count=30)
	return comments['items']


def sendMessages(users, message):
	""" int[] users, str message """
	for user in users:
		try:
			vk(api.messages.send, user_id=user, message=message)
			logger.debug("Succesfully sent the message to {}".format(user))
		except:
			logger.debug("Failed to send the message to {}".format(user))


if __name__ == "__main__":
	with ErrorManager("notify"):
		notify()
