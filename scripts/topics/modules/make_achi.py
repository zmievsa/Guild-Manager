""" Создание испытаний """

from lib.commands import achi_is_active
from lib.topics import Fields, getPhoto
from topics.errors import GMError
from lib.config import test_id
from lib.guilds import Achi


id = 35747510
group = test_id
comment_amount = 83


def getAction(text):
	return main


def getResponse(request):
	return "Испытание успешно создано."


def finish(request):
	pass


def main(request):
	mandatory_keys = {"название":"name", "иконка":"icon", "шкалы":"waves"}
	fields = Fields(request.text, mandatory_keys)
	editFields(fields)
	checkIfAchiIsActive()
	checkName(fields['name'])
	Achi.create(**fields)


def editFields(fields):
	fields['icon'] = getPhoto(fields['icon'])
	waves = fields['waves'].split(" ")
	fields['waves'] = [getPhoto(w) for w in waves]


def checkIfAchiIsActive():
	if achi_is_active:
		raise GMError("Невозможно добавлять испытания во время сезона.")


def checkName(name):
	if Achi(name=name).exists:
		raise GMError("<<{}>> уже существует.".format(name))
