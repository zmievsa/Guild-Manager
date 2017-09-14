""" Создание испытаний """

from lib.object_creation import createAchi
from lib.commands import achi_is_active
from topics.lib import Fields, getPhoto
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
	mandatory_keys = "название", "иконка", "шкалы"
	fields = Fields(request.text, mandatory_keys)
	editFields(fields)
	checkIfAchiIsActive()
	checkName(fields['название'])
	createAchi(*[fields[key] for key in fields.all_keys])


def editFields(fields):
	fields['иконка'] = getPhoto(fields['иконка'])
	waves = fields['шкалы'].split(" ")
	fields['шкалы'] = [getPhoto(w) for w in waves]


def checkIfAchiIsActive():
	if achi_is_active:
		raise GMError("Невозможно добавлять испытания во время сезона.")


def checkName(name):
	if Achi(name=name).exists:
		raise GMError("<<{}>> уже существует.".format(name))
