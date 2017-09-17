""" Набор средств для упрощенной работы с вконтакте """

from lib.config import offline_debug
from lib.config import data_folder
from lib.config import group_id
from lib.config import sleep_time
from lib.database import Database

import logging
import sys
from os import chdir
from os.path import dirname
from os.path import realpath
from time import sleep
from vk import API
from vk import Session
from vk.exceptions import VkAPIError


def makeLogger(file_name):
	logger = logging.getLogger('GM')
	logger.setLevel("DEBUG")
	fh = logging.FileHandler(file_name, mode="a")
	sh = logging.StreamHandler(stream=sys.stdout)
	fh_formatter = logging.Formatter('[%(asctime)s] %(name)s: %(message)s')
	sh_formatter = logging.Formatter('%(name)s: %(message)s')
	fh.setFormatter(fh_formatter)
	sh.setFormatter(sh_formatter)
	logger.addHandler(fh)
	logger.addHandler(sh)
	return logger


def getApi(token_path):
	""" Логинится в вк и возвращает готовую к работе сессию """
	with open(token_path) as f:
		token = f.read().strip()
		session = Session(access_token=token)
		return API(session, v='5.52', lang='ru')


def getToken():
	""" Создает токен для заданного приложения """
	import webbrowser as wb
	client_id = 5747467    # Id приложения
	scope = 2047391        # Код доступа, который мы запрашиваем
	standard_config = "display=page&redirect_uri=http://vk.com&response_type=token&v=5.60"
	url = "https://oauth.vk.com/authorize?"
	url += "client_id={}&{}&scope={}".format(
		client_id, standard_config, scope)
	wb.open(url, new=2)


def vk(method, suspend_time=sleep_time, **kwargs):
	""" Делает запрос к вк, ожидая необходимое время """
	if not offline_debug:
		sleep(suspend_time)
		return method(**kwargs)
	else:
		return {"items":[], "count":0}


def vkCaptcha(method, **kwargs):
	""" Не позволяет программе вылететь, когда вк просит ввести капчу """
	try:
		return vk(method, **kwargs)
	except VkAPIError:
		sleep(10)
		return vkCaptcha(method, **kwargs)


def getBanned(group_id):
	""" Возвращает список забаненных в сообществе пользователей """
	bans = vk(api.groups.getBanned, group_id=group_id)['items']
	banned = [user['id'] for user in bans if "id" in user]
	return banned


def setCurrentDirectory():
	""" Требуется при вызове скрипта не из его директории

		Меняет директорию на GM4/scripts вне зависимости
		от того, где они находятся, и где был вызван скрипт
	"""
	path = dirname(dirname(realpath(__file__)))
	chdir(path)


setCurrentDirectory()
logger = makeLogger(data_folder + "debug.log")
logger.debug("BEGINNING A NEW SESSION...")
logger.debug("Loading utils...")
api = getApi(data_folder + "token.txt")
ban_list = getBanned(group_id)
database = Database(data_folder + "database")
achi_is_active = database.getByField("config", field="id", value=1)["value"]
logger.debug("All utils loaded")
