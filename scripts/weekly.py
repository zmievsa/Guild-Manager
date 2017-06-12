#!/usr/bin/env python3

from os import listdir
from lib.commands import error, database
from lib.posts import editPost, getPostTime, post


def generate():
	""" Генерирует посты на неделю """
	days = getPlannedPosts()
	challenge = getNewChallenge()
	setThisWeekChallenge(challenge)
	for day in days:
		with open("../Data/week_posts/" + day, encoding="utf-8") as file:
			file = editPost(file.read(), challenge)
			digit = int(day[0])
			post_time = getPostTime(digit)
			post(file, post_time)


def getPlannedPosts():
	days = listdir("../Data/week_posts")
	return [d for d in days if ".txt" in d]


def getNewChallenge():
	""" Возвращает следующий в базе данных челлендж и вносит его в БД
		returns XML
	"""
	xml_field = getWeeklyChallengeField()
	old_challenge = int(xml_field.text)
	highest_id = getHighestChallengeId()
	new_challenge_id = getNextChallenge(old_challenge, highest_id)
	challenge = getChallengeElement(new_challenge_id)
	return challenge


def getWeeklyChallengeField():
	return database.find("challenges").find("this_week")


def getHighestChallengeId():
	challenges = database.getAll(kind="challenges", field="id")
	all_ids = [int(c) for c in challenges]
	return max(all_ids)


def getNextChallenge(old_challenge, highest_possible):
	if old_challenge == highest_possible:
		return "1"
	else:
		return str(old_challenge + 1)


def getChallengeElement(challenge_id):
	return database.getById(kind="challenges", id=challenge_id)


def setThisWeekChallenge(challenge):
	xml_field = getWeeklyChallengeField()
	challenge_id = challenge.find("id").text
	xml_field.text = challenge_id
	database.rewrite()


if __name__ == "__main__":
	try:
		generate()
	except Exception as e:
		error("weekly")
