#!/usr/bin/env python3

from lib.commands import api, database, vkCap
from lib.wiki_pages import updateGuild
from lib.guilds import Player
from lib.errors import *
from re import search


class Image(object):
	""" An approval or error image that we add to the comment """
	def __init__(self, link):
		self.link = link
		self.id = int(link.split("_")[1])


""" Константы """
failure_image = Image("photo98216156_456240031")	# Ссылка на фото, когда бот нашел ошибку
succeed_image = Image("photo98216156_456240030")	# Ссылка на фото, когда бот успешно все поменял
text_division = '_' * 27							# Разделение текста игрока и админа


class Request(object):
	def __init__(self, post_text, post_owner, comment_id, topic):
		self.id = comment_id
		self.topic = topic
		self.text = post_text
		self.asker = Player(post_owner)
		self.action = self.topic.getAction(self.text.lower())

	def process(self):
		""" Обрабатывает запрос """
		try:
			self.checkActionExistence()
			self.action(self)
		except GMError as e:
			self.message = e
			self.picture = failure_image.link
		else:
			self.message = self.topic.getMessage(self.text.lower(), self.asker)
			self.picture = succeed_image.link

	def finish(self):
		""" Завершает обработку и вносит изменения """
		database.rewrite()
		if self.asker.guild is not None:
			updateGuild(self.asker.get("guild"))
		self.addMessageToComment(self.message)
		self.editComment()

	def checkActionExistence(self):
		if self.action is None:
			raise wrong_request

	def addMessageToComment(self, message):
		self.text = "{}\n{}\n{}".format(self.text, text_division, message)

	def editComment(self):
		""" Оповещает игрока о результатах обработки заявки """
		vkCap(api.board.editComment,
			group_id=self.topic.group,
			topic_id=self.topic.id,
			comment_id=self.id,
			message=self.text,
			attachments=self.picture)


def getComments(topic, amount):
	""" Получение последних комментариев в обсуждении topic
		returns dict[]
	"""
	offset = 0
	for parse in range(2):
		response = api.board.getComments(
			group_id=topic.group,
			topic_id=topic.id,
			offset=offset,
			count=amount)
		comments = response['items']
		offset = response['count']
		offset -= amount
	return comments


class Hyperlink(object):
	def __init__(self, text):
		hyperlink = self.find(text)
		if hyperlink is None:
			raise hyperlink_wrong_format
		self.id, self.name = self.divide(hyperlink)
		checkNicknameFormat(self.name)

	def __repr__(self):
		return "[id{}|{}]".format(self.id, self.name)

	@staticmethod
	def find(text):
		pattern = r"\[id\d+\|.+\]"
		match = search(pattern, text)
		if match is not None:
			return match.group()

	@staticmethod
	def divide(hyperlink):
		hyperlink = hyperlink[3:-1]  # removes brackets [] and "id"
		id_, name = hyperlink.split("|")
		return id_, name


def checkNicknameFormat(name):
	if name is not None:
		nickname_format = GMError("Ник {} содержит недопустимые символы.".format(name))
		pattern = r"^[A-Za-z_\d]+$"
		match = search(pattern, name)
		if match is None:
			raise nickname_format
		elif not 20 >= len(name) >= 3:
			raise nickname_length
	else:
		raise nickname_format
