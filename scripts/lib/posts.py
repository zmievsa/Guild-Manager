""" Функции для работы с постами"""

from lib.config import group_id, data_folder
from datetime import datetime, timedelta
from lib.commands import api, vk
from pytz import timezone


def post(post_text, post_time, group_id=group_id):
	""" Публикует пост с таймером """
	try:
		post_id = vk(api.wall.post,
			owner_id=-group_id,
			from_group=1,
			message=post_text,
			publish_date=post_time)
	except:
		return post(post_text, post_time + 120)
	else:
		return post_id['post_id']


def getPostTime(digit=None):
	""" Возвращает время (unixtime) для поста

		Если аргумент получен, будет отправлено время, соответствующее
		18:00 дня. День определяется аргументом (например, digit=5 выдаст субботу)
		Если же аргумент не был получен, будет возвращено время через час
		после вызова функции.
	"""
	assert type(digit) is int
	hour = 3600
	day = timedelta(1)
	today = datetime.now(timezone('Europe/Moscow'))
	if digit:
		weekday = day.weekday()
		while weekday != digit:
			today += day
			weekday = day.weekday()
		today = day.replace(hour=18, minute=0, second=0)
		return int(day.timestamp())
	else:
		return int(day.timestamp()) + hour


def getText(file_name):
	""" Для получения смешнявых текстиков для постов

		'other' для любых текстов
		'results' для текстов к результатам ежа

		Функция берет первую строку файла,
		перемещает ее в конец и возвращает
	"""
	file_name = data_folder + "texts/{}.txt".format(file_name)
	with open(file_name, "r") as file:
		contents = file.readlines()
	phrase = "\n" + contents[0].strip()
	contents.pop(0)
	contents.append(phrase)
	with open(file_name, "w") as file:
		for line in contents:
			file.write(line)
		return phrase.strip()


def editPost(text, eweek=None):
	""" Заменяет стандартные поля поста на тексты/условия ежа """
	if "[текст]" in text:
		text = text.replace("[текст]", getText("other"))

	if "[условия]" in text:
		ch1, ch2, ch3 = eweek.challenges
		rules = str(eweek)
		text = text.replace("[условия]", rules)
		text = text.replace("[1]", ch1)
		text = text.replace("[2]", ch2)
		text = text.replace("[3]", ch3)
	return text
