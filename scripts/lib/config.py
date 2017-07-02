aottg_main = 64867627					# id группы aottg 4k
aottg_admin = 77675108					# id группы тест
aot_main = 57828226						# id группы aotg 7k
aot_admin = 114995030					# id группы ts_files
my_id = 98216156						# id аккаунта владельца
sleep_time = 0.5						# Время ожидания sleep()
database_path = "../Data/database.xml"	# путь к базе данных
token_path = "../Data/token.txt" 		# путь к токену
achi_is_active = False					# Работают ли ачи в этот момент времени


""" TOPICS """


class Image(object):
	def __init__(self, link):
		self.link = link
		self.id = int(link.split("_")[1])


failure_image = Image("photo98216156_456240031")	# Ссылка на фото, когда бот нашел ошибку
succeed_image = Image("photo98216156_456240030")	# Ссылка на фото, когда бот успешно все поменял
text_division = '_' * 27							# Разделение текста игрока и админа
