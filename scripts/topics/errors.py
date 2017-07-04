""" Ошибки, возвращаемые пользователю, который написал запрос в обсуждении """


class GMError(Exception):
	def __init__(self, message):
		self.message = message


need_head_rights = GMError("Недостаточно прав. Требуемый ранг: Глава")
need_vice_rights = GMError("Недостаточно прав. Требуемый ранг: Заместитель главы")
wrong_banner = GMError("Баннер имеет неправильный размер. Корректное соотношение: 500x60")
wrong_logo = GMError("Логотип имеет неправильный размер. Корректное соотношение: 200x200")
photo_not_found = GMError("Ссылка на изображение не найдена.")
need_photo_uploaded = GMError("Фото должно быть загружено в альбомы группы.")
wrong_request = GMError("Заявка оформлена неверно. Правила оформления: https://vk.com/page-64867627_50836585")
hyperlink_wrong_format = GMError("Гиперссылка оформлена неверно или отсутствует.")
not_in_guild = GMError("Игрок не состоит в гильдии.")
no_such_avatar = GMError("Аватар не существует.")
player_already_exists = GMError("Такой игрок уже существует.")
nickname_already_exists = GMError("Никнейм принадлежит другому игроку.")
nickname_length = GMError("Никнейм имеет некорректную длину. Он должен иметь от трех до двадцати символов.")
nickname_format = GMError("Никнейм содержит недопустимые символы. Допустимые символы: буквы латиницы, нижние подчеркивания и цифры.")
already_in_guild = GMError("Игрок уже состоит в гильдии.")
player_not_found = GMError("Игрок не найден.")
too_many_heads = GMError("В гильдии слишком много глав.")
too_many_vices = GMError("В гильдии слишком много заместителей.")
head_cant_leave = GMError("Глава не может быть исключен или понижен другим участником.")
head_must_present = GMError("В гильдии должен присутствовать хотя бы один глава.")
need_text = GMError("Текст не найден. Обратите внимание, что он должен быть заключен в кавычки.")
user_banned = GMError("Пользователь находится в черном списке сообщества.")

GB_guild_not_found = GMError("Гильдии с таким названием не существует.")
GB_wrong_request = GMError("Необходимо использовать слова 'победа' или 'поражение'.")
