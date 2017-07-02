#!/usr/bin/env python3

from lib.posts import editPost, getPostTime, post
from lib.errors import ErrorManager
from lib.commands import database
from lib.config import data_path
from lib.guilds import Eweek
from os import listdir


def generate():
	""" Генерирует посты на неделю """
	post_templates = getPlannedPosts()
	challenge = getNewChallenge()
	setThisWeekChallenge(challenge)
	makePosts(post_templates, challenge)


def makePosts(days, challenge):
	folder = data_path + "week_posts/"
	for day in days:
		with open(folder + day, encoding="utf-8") as file:
			file = editPost(file.read(), challenge)
			digit = int(day[0])
			post_time = getPostTime(digit)
			post(file, post_time)


def getPlannedPosts():
	days = listdir(data_path + "week_posts/")
	return [d for d in days if ".txt" in d]


def getNewChallenge():
	""" Возвращает следующий в базе данных челлендж и вносит его в БД
		returns XML
	"""
	xml_field = getWeeklyChallengeField()
	old_challenge = int(xml_field.text)
	highest_id = getHighestChallengeId()
	new_challenge_id = getNextChallenge(old_challenge, highest_id)
	challenge = getChallenge(new_challenge_id)
	return challenge


def getWeeklyChallengeField():
	return database.find("eweeks").find("this_week")


def getHighestChallengeId():
	challenges = database.getAll(kind="eweeks", field="id")
	all_ids = [int(c) for c in challenges]
	return max(all_ids)


def getNextChallenge(old_challenge, highest_possible):
	if old_challenge == highest_possible:
		return "1"
	else:
		return str(old_challenge + 1)


def getChallenge(challenge_id):
	return Eweek(challenge_id)


def setThisWeekChallenge(challenge):
	xml_field = getWeeklyChallengeField()
	challenge_id = challenge.get("id")
	xml_field.text = challenge_id
	database.rewrite()


if __name__ == "__main__":
	with ErrorManager("weekly"):
		generate()
