import sqlite3 as SQL
from logging import getLogger

logger = getLogger("GM.database")


class Database:
	def __init__(self, path):
		self.connect(path)

	def connect(self, path):
		self.path = path
		self.connection = SQL.connect(path)
		self.cursor = self.connection.cursor()

	def execute(self, expression, *args, **kwargs):
		logger.debug("{} (args: {}, kwargs: {})".format(expression, args, kwargs))
		self.cursor.execute(expression, *args, **kwargs)

	def save(self):
		""" Сохраняет базу данных """
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
			names = "({})".format(", ".join(names))
			expression = expression.format(table=parent, names=", ".join(names),
				values=makeQuestionMarks(args))
		self.execute(expression, args)

	def deleteElement(self, parent, id):
		expression = "DELETE FROM {table} WHERE id={id}".format(
			table=parent, id=id)
		self.execute(expression)


def makeQuestionMarks(args):
	return ", ".join(["?"] * len(args))
