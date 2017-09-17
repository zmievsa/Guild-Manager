""" Изменения в гильдиях """

from lib.commands import database, ban_list
from lib.wiki_pages import updateGuild
from lib.guilds import Player, Rank
from lib.config import group_id

from topics.lib import Hyperlink, checkNicknameFormat
from topics.errors import *
from re import search


id = 29901188
group = group_id
comment_amount = 83


def getAction(text):
	actions = {
		"ник":changeNick,
		"ссылку":changeId,
		"лого":changeLogo,
		"баннер":changeBanner,
		"аватар":changeAvatar,
		"статус":changeStatus,
		"описание":changeAbout,
		"вступлени":changeRequirements,
		"название гильдии":changeGuildName,
		"зачисли":addToGuild,
		"исключи":check_excludeFromGuild,
		"распустить гильдию":check_endGuild,
	}
	for pattern, action in actions.items():
		if pattern in text:
			return action


def getResponse(request):
	""" Возвращает сообщение, которое должен получить игрок """
	text, asker = request.text.lower(), request.asker
	guild_type = ("баннер", "лого", "название", "описание",
	"вступлени", "распустить", "исключи", "зачисли", "статус")
	player_type = ("ник", "ссылку", "аватар")
	if any(s in text for s in guild_type):
		message = "Гильдия: {}".format(asker.guild.name)
	elif any(s in text for s in player_type):
		message = "Игрок: [id{}|{}]".format(asker.id, asker.name)
	if "83" in text:
		message += "\n(HC)"
	return message


def finish(request):
	if request.asker.guild is not None:
		updateGuild(request.asker.guild_id)


def changeNick(request):
	"Прошу сменить мой никнейм на ..."
	name = getNickname(request.text)
	checkIfPlayerExists(name=name)
	if request.asker.exists:
		request.asker.set("name", name)
	else:
		Player().create(id=request.asker.id, name=name)


def changeId(request):
	"Прошу сменить мою ссылку на ..."
	hyperlink = Hyperlink(request.text)
	checkIfPlayerExists(id=hyperlink.id)
	if request.asker.exists:
		request.asker.set("id", hyperlink.id)
	else:
		Player().create(id=hyperlink.id, name=hyperlink.name)


def checkIfPlayerExists(id=None, name=None):
	player = Player(id, name)
	if player.exists:
		if id is not None:
			raise player_already_exists
		elif name is not None:
			raise nickname_already_exists


def changeAvatar(request):
	"Прошу сменить мой аватар на ..."
	if not request.asker.exists:
		raise player_not_found
	new_avatar = getNewAvatar(request.text)
	checkAvatar(new_avatar)
	request.asker.set("avatar", new_avatar)


def getNewAvatar(text):
	pattern = r"\d{1,3}"
	avatar_id = search(pattern, text)
	if avatar_id is None:
		raise wrong_request
	else:
		return avatar_id.group()


def checkAvatar(avatar_id):
	highest_id = getHighestAvatarId()
	if not highest_id >= int(avatar_id) >= 1:
		raise no_such_avatar


def getHighestAvatarId():
	all_avatars = database.getAll("avatars", "id")
	return max(all_avatars)


def changeStatus(request):
	"Прошу сменить статус ... на главу, заместителя, игрока"
	asker = request.asker
	guild = asker.guild
	heads, vices = guild.heads, guild.vices
	status = getRequestedStatus(request.text)
	hyperlink = Hyperlink(request.text)
	player = Player(hyperlink.id)
	if not player.exists or player.guild_id != asker.guild_id:
		raise not_in_guild
	elif not asker.inguild or not player.inguild:
		raise not_in_guild
	if "глав" in status:
		checkRights(asker, "head")
		if len(heads) == 2:
			raise too_many_heads
		else:
			guild.setPosition(player.id, "head")
	elif "зам" in status:
		checkRights(asker, "head")
		if len(vices) == 4:
			raise too_many_vices
		elif asker.id == player.id and len(heads) == 1:
			raise head_must_present
		elif asker.id != player.id and player.rank == Rank.head:
			raise head_cant_leave
		else:
			guild.setPosition(player.id, "vice")
	elif "игрок" in status:
		if asker.id == player.id and asker.rank == Rank.head and len(heads) == 1:
			raise head_must_present
		elif asker.id != player.id and asker.rank != Rank.head:
			raise need_head_rights
		elif asker.id != player.id and player.rank == Rank.head:
			raise head_cant_leave
		else:
			guild.setPosition(player.id, "player")


def getRequestedStatus(text):
	pattern = r"на (глав|зам|игрок)"
	match = search(pattern, text)
	if match is None:
		raise wrong_request
	status = match.group()[3:]
	return status


def changeLogo(request):
	"Прошу сменить логотип"
	checkRights(request.asker, "head")
	photo = getPhoto(request.text)
	request.asker.guild.set("logo", photo)


def changeBanner(request):
	"Прошу сменить баннер"
	checkRights(request.asker, "head")
	photo = getPhoto(request.text)
	request.asker.guild.set("banner", photo)


def getPhoto(text):
	photo = search(r"com/photo-\w+", text)
	if photo is None:
		raise photo_not_found
	else:
		photo = photo.group()[4:]
	if str(aottg_main) not in photo:
		raise need_photo_uploaded
	return photo


def changeGuildName(request):
	"Прошу сменить название гильдии на ..."
	checkRights(request.asker, "head")
	name = getNewGuildName(request.text)
	request.asker.guild.set("name", name)


def getNewGuildName(text):
	pattern = r"на [A-Za-z\d_ ]+(\.|$)"
	match = search(pattern, text)
	if match is None:
		raise wrong_request
	name = match.group()[3:]
	name = name.replace(".", "")
	return name


def changeAbout(request):
	"Прошу сменить описание гильдии на ..."
	checkRights(request.asker, "head")
	new = request.text.split("\"")
	if len(new) != 3:
		raise need_text
	request.asker.guild.set("about", new[1])


def changeRequirements(request):
	"Прошу сменить условия для вступления гильдии на ..."
	checkRights(request.asker, "head")
	new = request.text.split("\"")
	if len(new) != 3:
		raise need_text
	request.asker.guild.set("requirements", new[1])


def addToGuild(request):
	"Прошу зачислить игрока ..."
	checkRights(request.asker, "vice")
	guild_id = request.asker.guild_id
	hyperlink = Hyperlink(request.text)
	id_, name = hyperlink.id, hyperlink.name
	player = Player(id=id_)
	if id_ in ban_list:
		raise user_banned
	elif player.inguild:
		raise already_in_guild
	if player.exists:
		player.set("guild_id", guild_id)
	else:
		checkIfPlayerExists(name=name)
		Player().create(id=id_, name=name, guild_id=guild_id)


def check_excludeFromGuild(request):
	"Прошу исключить игрока ..."
	if not request.asker.inguild:
		raise not_in_guild
	asker = request.asker
	guild = asker.guild
	request.guilds_to_update.append(guild)
	if "меня" in request.text:
		if asker.rank == Rank.head and len(guild.heads) == 1:
			raise head_must_present
		excludeFromGuild(request.asker)
		return
	player = Player(Hyperlink(request.text).id)
	if player.guild_id != asker.guild_id:
		raise not_in_guild
	elif asker.rank <= player.rank:
		if player.rank == Rank.vice:
			raise need_head_rights
		elif player.rank == Rank.player:
			raise need_vice_rights
	elif player.rank == Rank.head:
		raise head_cant_leave
	excludeFromGuild(player)


def excludeFromGuild(player):
	player.guild.setPosition(player, "player")
	player.set("guild_id", 0)


def check_endGuild(request):
	"Прошу распустить гильдию."
	checkRights(request.asker, "head")
	endGuild(request.asker.guild_id)


def endGuild(guild_id):
	removePlayersFromGuild(guild_id)
	database.deleteElement("guilds", guild_id)


def removePlayersFromGuild(guild_id):
	players = [Player(id=id) for id in database.getAll("players", "id")]
	for player in players:
		if player.guild_id == guild_id:
			player.set("guild_id", 0)


def getNickname(text):
	hyperlink = Hyperlink.find(text)
	if hyperlink is not None:
		name = Hyperlink(text).name
	else:
		name = searchForNickname(text)
	checkNicknameFormat(name)
	return name


def searchForNickname(text):
	pattern = r"[A-Za-z_\d]+\.?$"
	match = search(pattern, text)
	if match is not None:
		name = match.group()
		name = name.replace(".", "")
		return name


def checkRights(player, position):
	if position == "head" and player.rank < Rank.head:
		raise need_head_rights
	elif position == "vice" and player.rank < Rank.vice:
		raise need_vice_rights
