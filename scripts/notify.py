#!/usr/bin/env python3

from lib.commands import api, group_id, sleep_time, getBanned, error
from time import sleep


def notify(test=False):
	""" Оповещает игроков о начале сервера или еженедельника """
	message = getMessage(test)
	users = getEweekPlayers()
	ban_list = getBanned()
	users = {user for user in users if user not in ban_list}
	sendMessages(users, message)


def getMessage(test):
	if test:
		message = "Тест"
	else:
		message = "Еженедельник начался, а ты как раз записался. Приходи, если ещё не сдал!\n"
		warning = "\n(Это автоматическое сообщение. Отвечать на него не нужно.)"
		message += warning
	return message


def getEweekPlayers():
	post = api.wall.search(owner_id=-group_id, query="#aottg83_reg", count=1)
	post_id = post['items'][0]['id']
	comments = api.wall.getComments(
		owner_id=-group_id, post_id=post_id, count=30)['items']
	users = {comment['from_id'] for comment in comments}
	return users


def sendMessages(users, message):
	""" int[] users, str message """
	for user in users:
		sleep(sleep_time)
		try:
			api.messages.send(user_id=user, message=message)
		except:
			pass


if __name__ == "__main__":
	try:
		notify()
	except:
		error("notify")
