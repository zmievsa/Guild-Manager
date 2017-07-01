from traceback import format_exception, format_exc
from lib.config import my_id
from lib.commands import api


class ErrorManager:
	def __init__(self, name, suspended=False):
		self.name = name
		self.suspended = suspended
		self.errors = []

	def __enter__(self):
		pass

	def __exit__(self, *args):
		if args[0] is not None:
			error = exc_info()[1]
			self.errors.append(error)
			if not self.suspended:
				self.finish()

	def finish(self):
		for error in self.errors:
			error(self.name)


def error(name, exception=None):
	exception = format_error(exception)
	message = "{}:\n{}".format(name, exception)
	api.messages.send(user_id=my_id, message=message)


def format_error(error):
	if error is not None:
		error_info = format_exception(type(error), error, error.__traceback__)
		return "".join(error_info)
	else:
		return format_exc()
