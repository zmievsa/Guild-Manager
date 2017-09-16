""" Создание еженедельников """

from lib.config import test_id
from topics.lib import Fields
from lib.guilds import Eweek


id = 35748154
group = test_id
comment_amount = 83


def getAction(text):
	return main


def getResponse(request):
	return "Еженедельник успешно создан."


def finish(request):
	pass


def main(request):
	mandatory_keys = {"карта":"map", "ч1":"ch1", "ч2":"ch2", "ч3":"ch3"}
	optional_keys = {"сложность":"diff", "цель":"goal", "дополнительно":"settings"}
	fields = Fields(request.text, mandatory_keys, optional_keys)
	Eweek().create(**fields)
