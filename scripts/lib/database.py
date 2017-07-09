""" Абстракция над lxml для упрощенной работы с базой данных """

from lxml.etree import ElementTree, XMLParser, parse


class Database:
	""" Необходимо использовать как singleton

		Иначе может произойти потеря данных при
		использовании двумя разными скриптами
	"""
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

	def getByField(self, parent, field, value):
		""" Ищет элемент в базе данных по одному из полей

			returns Element
		"""
		value = str(value).lower()
		elements = self.getAll(parent)
		for element in elements:
			subelement = element.find(field)
			if subelement is not None and subelement.text.lower() == value:
				return element

	def getById(self, parent, id):
		return self.getByField(parent, "id", id)

	def getByName(self, parent, name):
		return self.getByField(parent, "name", name)

	def getAll(self, parent, field=None):
		""" Возвращает список объектов или значения их атрибутов

			Args:
				str parent = контейнер (players, guilds, etc)
				str field = название атрибута

			returns Element[] or str[]

		"""
		parent = self.find(parent)
		if parent is not None:
			children = list(parent.iterchildren())
			if children != []:
				if field is not None:
					return self._getFields(field, children)
				else:
					return children

	def _getFields(self, field, children):
		fields = []
		for element in children:
			subelement = element.find(field)
			if subelement is not None:
				fields.append(subelement.text)
		return fields
