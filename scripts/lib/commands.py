""" Набор средств для упрощенной работы с вконтакте """

from vk.exceptions import VkAPIError
from vk import Session, API

from os.path import realpath
from os import chdir

from lib.config import sleep_time, group_id, data_folder
from lib.database import Database
from time import sleep


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


def vk(method, **kwargs):
	""" Делает запрос к вк, ожидая необходимое время """
	sleep(sleep_time)
	return method(**kwargs)


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
	path = realpath(__file__)
	index = path.index("/lib")
	path = path[:index]
	chdir(path)


setCurrentDirectory()
api = getApi(data_folder + "token.txt")
ban_list = getBanned(group_id)
database = Database(data_folder + "database.xml")
