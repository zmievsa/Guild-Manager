import sqlite3 as SQL


class Database:
	def __init__(self, path):
		self.connect(path)

	def connect(self, path):
		self.path = path
		self.connection = SQL.connect(path)
		self.cursor = self.connection.cursor()

	def rewrite(self):
		""" Сохраняет базу данных """
		self.connection.commit()

	def getByField(self, parent, field, value):
		""" Ищет элемент в базе данных по одному из полей """
		expression = "SELECT * FROM {table} WHERE {column}=?".format(
			table=parent, column=field)
		self.cursor.execute(expression, [value])
		return self.cursor.fetchone()

	def getAll(self, parent, field=None):
		""" Возвращает список объектов или значения их атрибутов """
		field = field or "*"
		expression = "SELECT {column} FROM {table}".format(table=parent, column=field)
		self.cursor.execute(expression)
		return self.cursor.fetchall()

	def setField(self, parent, id, field, value):
		expression = "UPDATE {table} SET {column}=? WHERE id={id}".format(
			table=parent, column=field, id=id)
		self.cursor.execute(expression, [value])

	def addElement(self, parent, args):
		question_marks = ", ".join(["?"] * len(args))
		expression = "INSERT into {table} VALUES({values})".format(
			table=parent, values=question_marks)
		self.cursor.execute(expression, args)

	def deleteElement(self, parent, id):
		expression = "DELETE FROM {table} WHERE id={id}".format(
			table=parent, id=id)
		self.cursor.execute(expression)
