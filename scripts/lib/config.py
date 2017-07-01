group_id = 64867627						# id основной группы
test_id = 77675108						# id группы 'тест'
my_id = 98216156						# id аккаунта владельца
sleep_time = 0.5						# Время ожидания sleep()
database_path = "../Data/database.xml"	# путь к базе данных
token_path = "../Data/token.txt" 		# путь к токену


""" TOPICS """


class Image(object):
	def __init__(self, link):
		self.link = link
		self.id = int(link.split("_")[1])


failure_image = Image("photo98216156_456240031")	# Ссылка на фото, когда бот нашел ошибку
succeed_image = Image("photo98216156_456240030")	# Ссылка на фото, когда бот успешно все поменял
text_division = '_' * 27							# Разделение текста игрока и админа
"""
	Прошу сменить мой ник на Zelda	<- Request
	___________________________ 	<- text_division
	Игрок: Zelda					<- Response
"""
