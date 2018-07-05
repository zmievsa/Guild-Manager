""" Набор средств для упрощенной работы с вконтакте """

from lib.config import data_folder
from lib.config import group_id
from lib.config import sleep_time
from lib.config import TOKEN_PATH
from lib.config import LOG_PATH
from lib.config import LOG_CONFIG_PATH
from lib.config import DATABASE_PATH
from lib.database import Database

import logging
import logging.config
import sys
from os import chdir
from os.path import dirname
from os.path import realpath
from time import sleep
import vk_api
import io


logger = logging.getLogger("GM")


def configureLogger(log_config_path, log_path):
	with open(log_config_path) as f:
		contents = f.read()
	file_like_obj = io.StringIO(contents.format(log_file=log_path))
	logging.config.fileConfig(file_like_obj)



def getApi(token_path):
	""" Логинится в вк и возвращает готовую к работе сессию """
	with open(token_path) as f:
		token = f.read().strip()
		session = vk_api.VkApi(token=token, api_version="5.52")
		return session.get_api()


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
	sleep(suspend_time)
	return method(**kwargs)
	# return {"items":[], "count":0}


def vkCaptcha(method, **kwargs):
	""" Не позволяет программе вылететь, когда вк просит ввести капчу """
	try:
		return vk(method, **kwargs)
	except vk_api.VkApiError:
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
configureLogger(LOG_CONFIG_PATH, LOG_PATH)
logger.debug("BEGINNING A NEW SESSION...")
api = getApi(TOKEN_PATH)
database = Database(DATABASE_PATH)
achi_is_active = database.getByField("config", field="id", value=1)["value"]
try:
	ban_list = getBanned(group_id)
except vk_api.VkApiError:
	logger.debug("Failed to load banlist")
	ban_list = []
logger.debug("All utils loaded")
