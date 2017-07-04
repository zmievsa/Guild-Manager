#!/usr/bin/env python3

from lib.posts import editPost, getPostTime, post
from lib.errors import ErrorManager
from lib.config import data_folder
from lib.commands import database
from lib.guilds import Eweek
from os import listdir


def generate():
	""" Генерирует посты на неделю """
	post_templates = getPlannedPosts()
	eweek = getNewEweek()
	setThisWeekEweek(eweek)
	makePosts(post_templates, eweek)
	database.rewrite()


def makePosts(days, eweek):
	""" Названия файлов соответствуют дням недели """
	folder = data_folder + "week_posts/"
	for day in days:
		with open(folder + day, encoding="utf-8") as file:
			file = editPost(file.read(), eweek)
			digit = int(day[0])
			post_time = getPostTime(digit)
			post(file, post_time)


def getPlannedPosts():
	days = listdir(data_folder + "week_posts/")
	return [d for d in days if ".txt" in d]


def getNewEweek():
	""" Возвращает следующий в базе данных еженедельник и вносит его в базу данных """
	xml_field = getWeeklyEweekField()
	old_eweek = int(xml_field.text)
	highest_id = getHighestEweekId()
	new_eweek_id = getNextEweek(old_eweek, highest_id)
	return Eweek(new_eweek_id)


def getWeeklyEweekField():
	return database.find("eweeks").find("this_week")


def getHighestEweekId():
	eweeks = database.getAll(kind="eweeks", field="id")
	all_ids = [int(e) for e in eweeks]
	return max(all_ids)


def getNextEweek(old_eweek, highest_possible):
	if old_eweek == highest_possible:
		return "1"
	else:
		return str(old_eweek + 1)


def setThisWeekEweek(eweek):
	xml_field = getWeeklyEweekField()
	xml_field.text = eweek.get("id")


if __name__ == "__main__":
	with ErrorManager("weekly"):
		generate()
