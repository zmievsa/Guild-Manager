""" Библиотека для работы с обсуждениями """

from lib.config import failure_image, succeed_image, text_division
from lib.commands import vk, api, vkCaptcha, database
from lib.wiki_pages import updateGuild
from lib.guilds import Player
from topics import errors
from re import search


class Request(object):
	""" Запрос пользователя к гильдменеджеру """
	def __init__(self, post_text, post_owner, comment_id, topic):
		self.id = comment_id
		self.topic = topic
		self.text = post_text
		self.asker = Player(post_owner)
		self.action = self.topic.getAction(self.text.lower())
		self.guilds_to_update = []

	def process(self):
		""" Обрабатывает запрос """
		try:
			self.checkActionExistence()
			self.action(self)
		except errors.GMError as e:
			self.message = e
			self.picture = failure_image.link
		else:
			self.message = self.topic.getResponse(self)
			self.picture = succeed_image.link

	def finish(self):
		""" Завершает обработку и вносит изменения """
		database.rewrite()
		self.topic.finish(self)
		self.updateGuilds()
		self.addMessageToComment(self.message)
		self.editComment()

	def checkActionExistence(self):
		if self.action is None:
			raise errors.wrong_request

	def updateGuilds(self):
		for guild in self.guilds_to_update:
			updateGuild(guild.get("id"))

	def addMessageToComment(self, message):
		self.text = "{}\n{}\n{}".format(self.text, text_division, message)

	def editComment(self):
		""" Оповещает игрока о результатах обработки заявки """
		vkCaptcha(api.board.editComment,
			group_id=self.topic.group,
			topic_id=self.topic.id,
			comment_id=self.id,
			message=self.text,
			attachments=self.picture)


def getComments(topic, amount):
	""" Получение последних комментариев в обсуждении topic """
	count = vk(api.board.getComments,
		group_id=topic.group,
		topic_id=topic.id,
		count=amount)['count']
	if count >= amount:
		offset = count - amount
	else:
		offset = 0
	response = vk(api.board.getComments,
		group_id=topic.group,
		topic_id=topic.id,
		offset=offset,
		count=amount)
	return response['items']


class Hyperlink(object):
	""" Ищет гиперссылку и проверяет ее по правилам группы """
	def __init__(self, text):
		hyperlink = self.find(text)
		if hyperlink is None:
			raise errors.hyperlink_wrong_format
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
		pattern = r"^[A-Za-z_\d]+$"
		match = search(pattern, name)
		if match is None:
			raise errors.GMError("Ник {} содержит недопустимые символы.".format(name))
		elif not 20 >= len(name) >= 3:
			raise errors.nickname_length
	else:
		raise errors.nickname_format


class Fields(dict):
	""" Получение полей из текста по ключам

		Вначале класс ищет поля в тексте по ключам. Далее
		он проверяет наличие ключей, кидает ошибку, если
		пропущены обязательные, и заполняет, если пропущены
		дополнительные. В конце он переводит ключи на
		английский, если ключи являются словарями.
	"""
	def __init__(self, text, mandatory_keys, optional_keys=None):
		if optional_keys is None:
			optional_keys = type(mandatory_keys)()
		super().__init__()
		self.text = text
		self.mandatory_keys = mandatory_keys
		self.optional_keys = optional_keys
		self.getAllKeys(mandatory_keys, optional_keys)
		self.makeFields()
		self.checkMandatoryFields()
		self.fillOptionalFields()
		if type(self.all_keys) is dict:
			self.translate()

	def getAllKeys(self, mand_keys, opt_keys):
		assert type(mand_keys) is type(opt_keys)
		if type(mand_keys) is dict:
			self.all_keys = dict(mand_keys, **opt_keys)
		else:
			self.all_keys = mand_keys + opt_keys

	def makeFields(self):
		text = self.text.splitlines()
		for line in text:
			if ":" in line:
				lower_line = line.lower()
				stripped_line = line[line.index(":") + 1:].strip()
				for key in self.all_keys:
					if key + ":" in lower_line:
						self[key] = stripped_line

	def checkMandatoryFields(self):
		for key in self.mandatory_keys:
			if key not in self:
				raise errors.GMError("Поле '{}' не найдено.".format(key))

	def fillOptionalFields(self):
		for key in self.optional_keys:
			if key not in self:
				self[key] = ""

	def translate(self):
		""" Переводит ключи на русский """
		keys = self.all_keys
		for russian_key in keys:
			english_key = keys[russian_key]
			self[english_key] = self[russian_key]
			self.pop(russian_key)


def getPhoto(text):
	""" Находит в тексте ссылку на изображение """
	pattern = r"photo-\d+_\d+"
	match = search(pattern, text)
	if match is not None:
		return match.group()
	else:
		raise errors.GMError("Некорректная ссылка на изображение.")
