""" Оповещение администратора о возникших ошибках """

from traceback import format_exception, format_exc
from lib.config import emergency_id
from lib.commands import vk, api


class ErrorManager:
	""" Упрощенное оповещение об ошибках

		str name: название скрипта (обычно укороченное)
		Использование: with ErrorManager(name): main()
	"""
	def __init__(self, name):
		self.name = name

	def __enter__(self):
		pass

	def __exit__(self, *args):
		if args[0] is not None:
			sendErrorMessage(self.name)


def sendErrorMessage(name, exception=None):
	""" Использует либо полученную ошибку, либо ту, что возникла последней """
	exception = format_error(exception)
	message = "{}:\n{}".format(name, exception)
	vk(api.messages.send, user_id=emergency_id, message=message)


def format_error(error):
	if error is not None:
		error_info = format_exception(type(error), error, error.__traceback__)
		return "".join(error_info)
	else:
		return format_exc()
