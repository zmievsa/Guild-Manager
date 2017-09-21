from topics.lib import Fields, getPhoto
from lib.config import group_id, test_id


id = 000
group = test_id
comment_amount = 83


def getAction(text):
	return main


def getResponse(request):
	return "Заявка успешна."


def finish(request):
	pass


def main(request):
	mandatory_keys = {"название":"name",}
	optional_keys = {}
	fields = Fields(request.text, mandatory_keys, optional_keys)
	editFields(fields)


def editFields(fields):
	pass
