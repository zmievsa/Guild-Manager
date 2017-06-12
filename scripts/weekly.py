#!/usr/bin/env python3

from os import listdir
from lib.commands import error, database
from lib.posts import editPost, getPostTime, post


def generate():
	""" Генерирует посты на неделю """
	days = getPlannedPosts()
	challenge = newChallenge()
	for day in days:
		with open("/home/varabe/GM4/Data/week_posts/" + day, encoding="utf-8") as file:
			file = editPost(file.read(), challenge)
			digit = int(day[0])
			post_time = getPostTime(digit)
			post(file, post_time)


def newChallenge():
	""" Возвращает следующий в базе данных челлендж и вносит его в БД
		returns XML

	"""
	challenges = database.getAll(kind="challenges", field="id")
	ids = [int(c) for c in challenges]
	highest_id = max(ids)
	lowest_id = min(ids)
	this_week = database.find("challenges").find("this_week").text
	this_week = int(this_week)
	if this_week + 1 > highest_id:
		challenge_id = str(lowest_id)
	else:
		challenge_id = str(this_week + 1)
	challenge = database.getById(kind="challenges", id=challenge_id)
	database.find("challenges").find("this_week").text = challenge_id
	database.rewrite()
	return challenge


def getPlannedPosts():
	days = listdir("/home/varabe/GM4/Data/week_posts")
	days = [d for d in days if ".txt" in d]
	return days


if __name__ == "__main__":
	try:
		generate()
	except Exception as e:
		error("weekly")
