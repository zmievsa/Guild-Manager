#!/usr/bin/env python3

from lib.commands import api, group_id, test_id, vkCap, database, ErrorManager
from lib.posts import getPostTime, getText, post
from lib.guilds import Eweek, Player
from re import search


def make():
	""" Создает пост с результатами еженедельника """
	players = getPlayers()
	challenges = getChallenges()
	players = sortPlayers(players, *challenges)
	post_text = createPost(players, challenges)
	post_time = getPostTime()
	post(post_text, post_time)


def getPlayers():
	comments = getEweekPostComments()
	participants = getParticipantsFromComments(comments)
	result_comments = getCommentsFromResultTopic()
	results = getResultsFromComments(result_comments)
	players = makePlayers(results, participants)
	return players


def getEweekPostComments():
	search_results = api.wall.search(owner_id=-group_id, query="#aottg83_reg", count=1)
	post_id = search_results['items'][0]['id']
	comments = api.wall.getComments(owner_id=-group_id, post_id=post_id, count=30)
	return comments['items']


def getParticipantsFromComments(comments):
	""" Возвращает ники и id записавшихся в словаре {ник:id} """
	participants = dict()
	for comment in comments:
		text = comment['text'].splitlines()
		from_id = comment['from_id']
		participants[text[0]] = from_id
		if len(text) > 1: # Если человек сначала написал ги, а потом ник
			participants[text[1]] = from_id
	return participants


def getCommentsFromResultTopic():
	""" Result topic -- тот, где мы пишем результаты участников """
	topic_id = 35693273
	response = api.board.getComments(
		topic_id=topic_id,
		group_id=test_id,
		count=50)
	return response['items']


def getResultsFromComments(comments):
	comments = [c['text'] for c in comments]
	pattern = r"\w+( \w+)? \d+" # Ник второйник? результат
	results = []
	for comment in comments:
		if search(pattern, comment):
			players = getPlayersFromComment(comment)
			results.append(players)
	return results


def getPlayersFromComment(comment):
	comment = comment.split(" ")
	player1 = Player(name=comment[0])
	if len(comment) > 2:
		player2 = Player(name=comment[1])
		player1.score = eval(comment[2])
		return player1, player2
	else:
		player1.score = eval(comment[1])
		return [player1]


def makePlayers(results, participants):
	for pair in results:
		for player in pair:
			if player.name in participants:
				name = player.name
				id = participants[player.name]
				player.recreate(id, name)
				if player.guild:
					guild = player.guild.get("name")
					player.guild = "[" + guild + "]"
			if not player.guild:
				player.guild = ""
	return results


def getChallenges():
	eweek_id = database.find("eweeks").find("this_week").text
	eweek = Eweek(eweek_id)
	challenges = eweek.get("ch1", "ch2", "ch3")
	return [int(ch) for ch in challenges]


def sortPlayers(players, ch1, ch2, ch3):
	if ch1 > ch2:
		reverse = True
	else:
		reverse = False
	players.sort(key=lambda x: x[0].score, reverse=reverse)
	return players


def getMessages():
	""" Возвращает список словарей-сообщений с результатами ежа """
	peer_id = vkCap(api.messages.search, q="#AoTTG_Eweek", count=1)
	peer_id = peer_id['items'][0]['chat_id']
	peer_id += 2000000000
	messages = vkCap(api.messages.getHistory, peer_id=peer_id, count=50)['items']
	return messages


def createPost(players, challenges):
	""" Создает пост с результатами ежа """
	post = "#aottg83_results\n"
	post += getText("results") + "\n\n"
	post += makeResults(players, challenges)
	post += "\n\nПравила еженедельника: https://vk.com/page-64867627_47291741?f=Еженедельник"
	return post


def makeResults(players, challenges):
	compare = compareChallenges(*challenges)
	post = ""
	current_row = "first"
	for index, pair in enumerate(players, start=1):
		score = pair[0].score
		line = "\n"
		line += makeFancyResult(index, pair, score)

		if index <= 3:
			pair_row = "first"
		else:
			pair_row = getPairRow(compare, score, *challenges)
		if current_row != pair_row:
			post += "\n"
		current_row = pair_row
		post += line
	return post


def compareChallenges(ch1, ch2, ch3):
	""" Возвращает функцию для сравнения результатов ежа

		Compare будет сравнивать челленджи с результатами,
		определяя, будет ли лучшим больший или меньший результат
	"""
	if ch1 > ch2:
		compare = lambda x, y: x >= y
	else:
		compare = lambda x, y: x <= y
	return compare


def makeFancyResult(index, pair, score):
	""" Создает строку с результатом пары и гильдией

		Место игрока) гиперссылка -- результат [гильдия]
		1) [id47|Varabe] -- 83 [SunseT]
	"""
	result = ""
	if len(pair) > 1:
		result += "{}) {} & {} -- {}".format(index, pair[0], pair[1], score)
	else:
		result += "{}) {} -- {}".format(index, pair[0], score)
	for player in pair:
		if player.guild:
			result += " " + player.guild
	return result


def getPairRow(compare, score, ch1, ch2, ch3):
	""" Ряды нужны для разделения игроков по челленджам """
	if compare(score, ch1):
		return "first"
	elif compare(score, ch2):
		return "second"
	elif compare(score, ch3):
		return "third"
	else:
		return "fourth"


if __name__ == "__main__":
	with ErrorManager("eweek"):
		make()
