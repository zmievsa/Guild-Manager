from traceback import format_exception, format_exc
from lib.commands import vk, api
from lib.config import my_id


class ErrorManager:
	def __init__(self, name):
		self.name = name

	def __enter__(self):
		pass

	def __exit__(self, *args):
		if args[0] is not None:
			sendErrorMessage(self.name)


def sendErrorMessage(name, exception=None):
	exception = format_error(exception)
	message = "{}:\n{}".format(name, exception)
	vk(api.messages.send, user_id=my_id, message=message)


def format_error(error):
	if error is not None:
		error_info = format_exception(type(error), error, error.__traceback__)
		return "".join(error_info)
	else:
		return format_exc()
