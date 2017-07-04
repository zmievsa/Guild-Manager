""" Набор констант, необходимых для работы гильдменеджера """

group_id = 64867627						# id группы aottg 4k
test_id = 77675108						# id группы тест
my_id = 98216156						# id аккаунта владельца
sleep_time = 0.5						# Время ожидания sleep()
data_folder = "../Data/"				# Путь от GM4/scripts к GM4/Data
achi_is_active = False					# Работают ли ачи в этот момент времени


""" TOPICS """

class Image(object):
	""" Упрощенное взаимодействие с атрибутами изображений """
	def __init__(self, link):
		self.link = link
		self.id = int(link.split("_")[1])

failure_image = Image("photo-77675108_456239404")	# Ссылка на фото, когда ГМ нашел ошибку
succeed_image = Image("photo-77675108_456239403")	# Ссылка на фото, когда ГМ успешно все поменял
text_division = '_' * 27							# Разделение текста игрока и админа
