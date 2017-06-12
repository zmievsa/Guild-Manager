#!/usr/bin/env python3

from lib.commands import api, group_id, vkCap, error, database
from lib.posts import getPostTime, getText, post as post_func
from re import search


class Player(object):
	def __init__(self, name):
		self.name = name
		self.hyperlink = name
		self.id = ""
		self.guild = ""


def make():
	""" Создает пост с результатами еженедельника """
	post = getEweekPost()
	first, second, third = getChallenges(post)
	compare, reverse = compareChallenges(first, second)
	participants = getParticipants(post)
	messages = getMessages()
	results = getResults(messages, reverse)
	players = checkParticipants(results, participants)
	post_text = createPost(players, compare, first, second, third)
	post_time = getPostTime()
	post_func(post_text, post_time)


def getEweekPost():
	post = api.wall.search(owner_id=-group_id, query="#aottg83_reg", count=1)
	post = post['items'][0]
	return post


def getChallenges(post):
	""" Ищет челленджи в тексте поста

		Args:
		str post

		returns int[] challenges

	"""
	text = post['text'].splitlines()
	challenges = []
	for line in text:
		if "челлендж: " in line:
			challenge = line[line.index(":") + 1:]
			challenges.append(eval(challenge))
	return challenges


def compareChallenges(first, second):
	""" Возвращает функцию и bool для сравнения результатов

		Args:
		int first = первый челлендж
		int second = второй челлендж

		Compare будет сравнивать челленджи с результатами,
		определяя, будет ли лучшим больший или меньший результат
		Reverse нужен для сортировки результатов

		returns lambda compare, bool reverse

	"""
	if first > second:
		compare = lambda x, y: x >= y
		reverse = True
	else:
		compare = lambda x, y: x <= y
		reverse = False
	return compare, reverse


def getParticipants(post):
	""" Возвращает словарь с именами записывашхися и их id"""
	comments = api.wall.getComments(
		owner_id=-64867627, post_id=post['id'], count=30)['items']
	participants = dict()
	for comment in comments:
		text = comment['text'].splitlines()
		from_id = comment['from_id']
		participants[text[0]] = from_id
		if len(text) > 1 and text[0] != text[1]:  # 'and' на всякие пожарные
			participants[text[1]] = from_id
	return participants


def getMessages():
	""" Возвращает список словарей-сообщений с результатами ежа """
	peer_id = vkCap(api.messages.search, q="#AoTTG_Eweek", count=1)
	peer_id = peer_id['items'][0]['chat_id']
	peer_id += 2000000000
	messages = vkCap(api.messages.getHistory, peer_id=peer_id, count=50)['items']
	return messages


def getResults(messages, reverse):
	""" Берет результаты и имена из сообщений

		Args:
		dict[] messages = список сообщений
		bool reverse = для функции sort()

		returns Player[][]

	"""
	results = []
	for message in messages:
		if message['body']:
			player = message['body']
		elif message.get('fwd_messages', False):
			player = message['fwd_messages'][0]['body']
		else:
			continue
		if search(r"\w+( \w+)? \d+", player):
			player = player.split(" ")
			player[0] = Player(player[0])
			if len(player) > 2:
				player[1] = Player(player[1])
				result = player[2]
			else:
				result = player[1]
			player.pop()
			player[0].result = eval(result)
			results.append(player)

	results.sort(key=lambda x: x[0].result, reverse=reverse)
	return results


def checkParticipants(results, participants):
	""" Сверяет имена игроков в результатах с записавшимися

		Args:
		Player[][] results = список пар (игроков)
		dict[] participants = ключи-имена, значения-id

		returns Player[][]

	"""
	for pair in results:
		for player in pair:
			if player.name in participants:
				player.id = str(participants[player.name])
				player.hyperlink = "[id{}|{}]".format(
					player.id, player.name)
				player_element = database.getById(kind="players", id=player.id)
				if player_element is not None:
					guild_id = player_element.find("guild").text
					guild = database.getField(
						kind="guilds", id=guild_id, field="name")
					if guild is not None and guild.text:
						player.guild = guild.text
	return results


def createPost(players, compare, first, second, third):
	""" Создает пост с результатами ежа

		Args:
		Players[][] players = список игроков
		lambda compare = сравнивает результаты и челленджи
		int first, second, third = челленджи

		returns str post
	"""
	post = "#aottg83_results\n"
	post += getText("results") + "\n\n"
	challenge = 1
	for index, pair in enumerate(players, start=1):
		line = "\n"
		if len(pair) > 1:
			line += "{}) {} & {} -- {}".format(
				index, pair[0].hyperlink, pair[1].hyperlink, pair[0].result)
		else:
			line += "{}) {} -- {}".format(
				index, pair[0].hyperlink, pair[0].result)

		for player in pair:
			if player.guild:
				line += " [{}]".format(player.guild)

		if index <= 3:
			new_challenge = 1
		else:
			if compare(pair[0].result, first):
				new_challenge = first
			elif compare(pair[0].result, second):
				new_challenge = second
			elif compare(pair[0].result, third):
				new_challenge = third
			else:
				new_challenge = 0

		if challenge != new_challenge:
			post += "\n"
		challenge = new_challenge
		post += line
	post += "\n\nПравила еженедельника: https://vk.com/page-64867627_47291741?f=Еженедельник"
	return post


if __name__ == "__main__":
	try:
		make()
	except:
		error("eweek")
