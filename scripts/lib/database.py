from lxml.etree import ElementTree, XMLParser, parse


class Database(object):
	def __init__(self, path):
		self.parse(path)

	def parse(self, path):
		parser = XMLParser(remove_blank_text=True, encoding="UTF-8")
		self.contents = parse(path, parser).getroot()
		self.path = path

	def find(self, string):
		return self.contents.find(string)

	def rewrite(self, recursion=True):
		""" Дважды записывает измененную базу данных в файл

			Двойное записывание и рекурсия -- костыль, нужный
			для того, чтобы сработал pretty_print

		"""
		tree = ElementTree(self.contents)
		tree.write(self.path, pretty_print=True, encoding="UTF-8")
		if recursion:
			database = Database(self.path)
			database.rewrite(recursion=False)

	def getByField(self, kind, field, value):
		""" Ищет элемент в базе данных по одному из полей

			Args:
			str kind = вид элемента (players, guilds, challenges)
			str/int field = одно из полей элемента, который мы ищем

			returns Element

		"""
		value = str(value).lower()
		iterator = self.find(kind).iterchildren()
		for element in iterator:
			subelement = element.find(field)
			if subelement is not None and subelement.text.lower() == value:
				return element

	def getById(self, kind, id):
		return self.getByField(kind, "id", id)

	def getByName(self, kind, name):
		return self.getByField(kind, "name", name)

	def getField(self, kind, id, field):
		""" Возвращает атрибут объекта по id

			Args:
			str kind = вид элемента (player, guild, challenge)
			str/int id = id элемента
			str field = название атрибута

			returns Element

		"""
		element = self.getById(kind, id)
		if element is not None:
			return element.find(field)

	def editField(self, kind, id, field, value):
		""" Изменить один из атрибутов объекта """
		field = self.getField(kind, id, field)
		field.text = value

	def getAll(self, kind, field=None):
		""" Возвращает список атрибутов одного типа объектов

			Args:
			str kind = вид элемента (player, guild, challenge)
			str field = название атрибута

			returns Element[]

		"""
		iterator = self.find(kind)
		if iterator is not None and list(iterator.iterchildren()) != []:
			iterator = iterator.iterchildren()
			if field is not None:
				lst = []
				for element in iterator:
					subelement = element.find(field)
					if subelement is not None:
						lst.append(subelement.text)
				return lst
			else:
				return list(iterator)
