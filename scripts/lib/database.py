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
		logger.debug(expression)
		self.cursor.execute(expression, *args, **kwargs)

	def rewrite(self):
		""" Сохраняет базу данных """
		self.connection.commit()

	def getByField(self, parent, field, value):
		""" Ищет элемент в базе данных по одному из полей """
		expression = "SELECT * FROM {table} WHERE {column}=?".format(
			table=parent, column=field)
		self.execute(expression, [value])
		description = [d[0] for d in self.cursor.description]
		return self.cursor.fetchone(), description

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

	def addElement(self, parent, args):
		question_marks = ", ".join(["?"] * len(args))
		expression = "INSERT into {table} VALUES({values})".format(
			table=parent, values=question_marks)
		self.execute(expression, args)

	def deleteElement(self, parent, id):
		expression = "DELETE FROM {table} WHERE id={id}".format(
			table=parent, id=id)
		self.execute(expression)
