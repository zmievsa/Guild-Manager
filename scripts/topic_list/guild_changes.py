from lib.commands import group_id, database, getBanned
from lib.topics import Hyperlink, checkNicknameFormat
from lib.guilds import createPlayer, Player
from lib.errors import *
from re import search


id = 29901188
group = group_id
ban_list = getBanned()
comment_amount = 20


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
	"исключи":excludeFromGuild,
	"распустить гильдию":endGuild,
	}
	for pattern, action in actions.items():
		if pattern in text:
			return action


def getMessage(text, asker):
	""" Возвращает сообщение, которое должен получить игрок """
	guild_type = ("баннер", "логотип", "название", "описание",
	"вступлени", "распустить", "исключи", "зачисли", "статус")
	player_type = ("ник", "ссылку", "аватар")
	if any(s in text for s in guild_type):
		guild_name = asker.guild.get("name")
		message = "Гильдия: {}".format(guild_name)
	elif any(s in text for s in player_type):
		id, name = asker.get("id", "name")
		message = "Игрок: [id{}|{}]".format(id, name)
	return message


def changeNick(request):
	"Прошу сменить мой никнейм на ..."
	name = getNickname(request.text)
	checkIfPlayerExists(name=name)
	if request.asker.exists:
		request.asker.set("name", name)
	else:
		createPlayer(id=request.asker.id, name=name)


def changeId(request):
	"Прошу сменить мою ссылку на ..."
	hyperlink = Hyperlink(request.text)
	checkIfPlayerExists(id=hyperlink.id)
	if request.asker.exists:
		request.asker.set("id", hyperlink.id)
	else:
		createPlayer(id=hyperlink.id, name=hyperlink.name)


def checkIfPlayerExists(id=None, name=None):
	if id:
		player = Player(id=id)
		if player.exists:
			raise player_already_exists
	elif name:
		player = Player(name=name)
		if player.exists:
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
	all_avatars = database.getAll(kind="avatars", field="id")
	all_avatars = (int(a) for a in all_avatars)
	return max(all_avatars)


def changeStatus(request):
	"Прошу сменить статус ... на главу, заместителя, игрока"
	asker = request.asker
	guild = asker.guild
	heads, vices = guild.heads, guild.vices
	status = getRequestedStatus(request.text)
	hyperlink = Hyperlink(request.text)
	player = Player(hyperlink.id)
	if not player.exists or player.get("guild") != asker.get("guild"):
		raise not_in_guild
	elif not asker.inguild or not player.inguild:
		raise not_in_guild
	if "глав" in status:
		if asker.rank != 3:
			raise need_head_rights
		elif len(heads) == 2:
			raise too_many_heads
		else:
			guild.setPosition(player.id, "head")
	elif "зам" in status:
		if asker.rank != 3:
			raise need_head_rights
		elif len(vices) == 4:
			raise too_many_vices
		elif asker.id == player.id and len(heads) == 1:
			raise head_must_present
		elif asker.id != player.id and player.rank == 3:
			raise head_cant_leave
		else:
			guild.setPosition(player.id, "vice")
	elif "игрок" in status:
		if asker.id == player.id and asker.rank == 3 and len(heads) == 1:
			raise head_must_present
		elif asker.id != player.id and asker.rank != 3:
			raise need_head_rights
		elif asker.id != player.id and player.rank == 3:
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
	if str(group_id) not in photo:
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
	guild_id = request.asker.guild.get("id")
	hyperlink = Hyperlink(request.text)
	id_, name = hyperlink.id, hyperlink.name
	player = Player(id_)
	if int(id_) in ban_list:
		raise user_banned
	elif player.inguild:
		raise already_in_guild
	if player.exists:
		player.set("guild", guild_id)
	else:
		checkIfPlayerExists(name=name)
		createPlayer(name=name, id=id_, guild=guild_id)


def excludeFromGuild(request):
	"Прошу исключить игрока ..."
	if not request.asker.inguild:
		raise not_in_guild
	asker = request.asker
	guild = asker.guild
	if "меня" in request.text:
		if asker.rank == 3 and len(guild.heads) == 1:
			raise head_must_present
		guild.setPosition(asker.id, "player")
		asker.set("guild", "0")
		return
	hyperlink = Hyperlink(request.text)
	player = Player(hyperlink.id)
	if player.get("guild") != asker.get("guild"):
		raise not_in_guild
	elif asker.rank != 3:
		raise need_head_rights
	elif player.rank == 3:
		raise head_cant_leave
	else:
		player.set("guild", "0")


def endGuild(request):
	"Прошу распустить гильдию."
	checkRights(request.asker, "head")
	guild = request.asker.guild
	guild_id = guild.get("id")
	removePlayersFromGuild(guild_id)
	deleteGuildElement(guild)


def removePlayersFromGuild(guild_id):
	players = database.find("players").iterchildren()
	for player in players:
		if player.find("guild").text == guild_id:
			player.find("guild").text = "0"


def deleteGuildElement(guild):
	parent = guild.xml_element.getparent()
	parent.remove(guild.xml_element)


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
	if position == "head" and player.rank < 3:
		raise need_head_rights
	elif position == "vice" and player.rank < 2:
		raise need_vice_rights
