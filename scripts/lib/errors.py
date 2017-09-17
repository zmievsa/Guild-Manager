""" Оповещение администратора о возникших ошибках """

from traceback import format_exception, format_exc
from contextlib import contextmanager
from lib.config import emergency_id
from lib.commands import vk, api
from logging import getLogger

logger = getLogger("GM.lib.errors")


@contextmanager
def ErrorManager(name):
	""" Упрощенное оповещение об ошибках

	str name: название скрипта (обычно укороченное)
	Использование: with ErrorManager(name): main()
	"""
	try:
		yield
	except Exception as e:
		logger.exception("Exception occured, exiting...")
		sendErrorMessage(name)
		raise e


def sendErrorMessage(name, exception=None):
	""" Использует либо полученную ошибку, либо ту, что возникла последней """
	logger.debug("Sending error message...")
	exception = format_error(exception)
	message = "{}:\n{}".format(name, exception)
	vk(api.messages.send, user_id=emergency_id, message=message)


def format_error(error):
	if error is not None:
		error_info = format_exception(type(error), error, error.__traceback__)
		return "".join(error_info)
	else:
		return format_exc()
