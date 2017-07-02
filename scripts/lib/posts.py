# -*- coding: utf-8 -*-

"""
Эта библиотека содержит инструменты для работы с постами в
"https://www.vk.com/attack_on_titan_tribute_game"

"""

from lib.config import aottg_main, sleep_time
from datetime import datetime, timedelta
from lib.commands import api
from pytz import timezone
from time import sleep


def post(post_text, post_time, group_id=aottg_main):
	""" Кидает пост в отложку

		str post_text
		int post_time (unixtime)

		returns int post_id

	"""
	sleep(sleep_time)
	try:
		post_id = api.wall.post(
			owner_id=-group_id,
			from_group=1,
			message=post_text,
			publish_date=post_time)
	except:
		return post(post_text, post_time + 120)
	else:
		return post_id['post_id']


def getPostTime(digit=None):
	""" Возвращает время (unixtime) для поста, исходя из аргумента

		Если аргумент получен, будет отправлено время, соответствующее
		18:00 дня, соответствующего числу (например, digit=5 выдаст субботу)
		Если же аргумент не был получен, будет возвращено время через час
		после вызова функции.

		returns int
	"""
	assert type(digit) is not str
	day = datetime.now(timezone('Europe/Moscow'))
	if digit:
		weekday = day.weekday()
		while weekday != digit:
			day += timedelta(1)
			weekday = day.weekday()
		day = day.replace(hour=18, minute=0, second=0)
		return int(day.timestamp())
	else:
		return int(day.timestamp()) + 3600


def getText(file_name):
	""" Для получения смешнявых текстиков для постов

		"other" для любых текстов
		'results' для текстов к результатам ежа

		returns str

	"""
	file_name = "../../Data/texts/{}.txt".format(file_name)
	with open(file_name, "r+") as file:
		new_file = file.readlines()
		phrase = "\n" + new_file[0].strip()
		new_file.pop(0)
		new_file.append(phrase)
		file.seek(0)
		file.truncate()
		for line in new_file:
			file.write(line)
		return phrase.strip()


def editPost(text, eweek=None):
	if "[текст]" in text:
		text = text.replace("[текст]", getText("other"))

	if "[условия]" in text:
		ch1, ch2, ch3 = getEweekChallenges(eweek)
		rules = getEweekRules(eweek)
		text = text.replace("[условия]", rules)
		text = text.replace("[1]", ch1)
		text = text.replace("[2]", ch2)
		text = text.replace("[3]", ch3)
	return text


def getEweekChallenges(eweek):
	return eweek.get("ch1", "ch2", "ch3")


def getEweekRules(eweek):
	config = eweek.get("map", "diff", "goal", "settings")
	rules = "{} {}, {} {}".format(*config)
	if not config[2]: # Нет цели = запятая не нужна :3
		rules = rules.replace(",", "")
	return rules
