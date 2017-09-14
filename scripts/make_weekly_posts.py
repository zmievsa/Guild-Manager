#!/usr/bin/env python3

from lib.posts import editPost, getPostTime, post
from lib.errors import ErrorManager
from lib.config import data_folder
from lib.commands import database
from logging import getLogger
from lib.guilds import Eweek
from os import listdir

logger = getLogger("GM.weekly_posts")


def generate():
	""" Генерирует посты на неделю """
	logger.debug("Generating weekly posts...")
	post_templates = getPlannedPosts()
	eweek = getNewEweek()
	setThisWeekEweek(eweek)
	makePosts(post_templates, eweek)
	database.save()


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
	return Eweek(id=new_eweek_id)


def getWeeklyEweekField():
	# FIX CALLS TO XML
	return database.find("eweeks").find("this_week")


def getHighestEweekId():
	eweek_ids = database.getAll(parent="eweeks", field="id")
	return max(eweek_ids)


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
