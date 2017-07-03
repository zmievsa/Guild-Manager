from lib.config import test_id, achi_is_active
from topics.lib import Fields


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
	checkIfAchiIsActive()
	mandatory_keys = {"название":"name", "иконка":"icon", "шкалы":"waves"}
	fields = Fields(request.text, mandatory_keys)
	editFields(fields)
	checkName(fields['name'])
	createAchi(**fields)


def checkIfAchiIsActive():
	if achi_is_active:
		raise GMError("Невозможно добавлять испытания во время сезона.")


def editFields(fields):
	fields['icon'] = getPhoto(fields['icon'])
	waves = fields['waves'].split(" ")
	fields['waves'] = [getPhoto(w) for w in waves]


def checkName(name):
	if Achi(name=name).exists:
		raise GMError("<<{}>> уже существует.".format(name))
