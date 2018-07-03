import sqlite3 as SQL
from logging import getLogger
from os.path import exists, isfile

logger = getLogger("GM.database")


class Database:
	def __init__(self, path):
		self.path = path
		self.checkFileExistence()
		self.connect()

	def connect(self):
		self.connection = SQL.connect(self.path)
		self.cursor = self.connection.cursor()

	def checkFileExistence(self):
		if not (exists(self.path) and isfile(self.path)):
			raise FileNotFoundError("Database not found:" + self.path)

	def execute(self, expression, *args, **kwargs):
		return self.cursor.execute(expression, *args, **kwargs)

	def save(self):
		self.connection.commit()

	def getByField(self, parent, field, value):
		""" Ищет элемент в базе данных по одному из полей """
		expression = "SELECT * FROM {table} WHERE {column}=?".format(
			table=parent, column=field)
		self.execute(expression, [value])
		description = (d[0] for d in self.cursor.description)
		response = self.cursor.fetchone()
		if response:
			response = dict(zip(description, response))
		return response

	def getAll(self, parent, field=None):
		""" Возвращает список объектов или значения их атрибутов """
		field = field or "*"
		expression = "SELECT {column} FROM {table}".format(table=parent, column=field)
		self.execute(expression)
		lst = self.cursor.fetchall()
		if field != "*":
			lst = [tuple_[0] for tuple_ in lst]
		return lst

	def setField(self, parent, id, field, value):
		expression = "UPDATE {table} SET {column}=? WHERE id={id}".format(
			table=parent, column=field, id=id)
		self.execute(expression, [value])

	def addElement(self, parent, args=None, kwargs=None):
		expression = "INSERT into {table} {names} VALUES({values})"
		if args:
			expression = expression.replace("{names}", "")
			expression = expression.format(table=parent, values=makeQuestionMarks(args))
		elif kwargs:
			names, args = kwargs.keys(), kwargs.values()
			# sqlite doesn't support all types of iterables
			# If you send 'dict_values[]' as args -- exception occurs
			args = list(args)
			names = "({})".format(", ".join(names))
			expression = expression.format(table=parent, names=names,
				values=makeQuestionMarks(args))
		return self.execute(expression, args).lastrowid

	def deleteElement(self, parent, id):
		expression = "DELETE FROM {table} WHERE id={id}".format(
			table=parent, id=id)
		self.execute(expression)


def makeQuestionMarks(args):
	return ", ".join(["?"] * len(args))
