from lib.commands import api, vkCap, database
from lib.config import group_id
import lxml.etree as ET


def genChallenges():
	database = Database(path="/home/varabe/GM4/Data/database.xml")
	challenges_tree = database.find("challenges")
	challenges = challenges_tree.findall("challenge")
	for challenge in challenges:
		challenges_tree.remove(challenge)
	with open("/home/varabe/GM4/Data/challenges.txt", "r") as file:
		for line in file.readlines():
			line = line.strip()
			map, diff, goal, ch1, ch2, ch3, *settings = line.split("|")
			settings = settings[0] if settings else None
			database.createChallenge(map=map, diff=diff, goal=goal,
				ch1=ch1, ch2=ch2, ch3=ch3, settings=settings)
	database.rewrite()


def genGuilds():
	import re
	""" Парсит гильдии, сохраняя имена игроков вместе с гильдиями в файл """
	if database.find("guilds") is not None:
		database.contents.remove("guilds")
	guilds = ET.SubElement(database.contents, "guilds")
	guilds_page = api.pages.get(
		page_id=47292063, group_id=group_id, need_source=1)
	guilds_page = guilds_page['source'].splitlines()
	guilds = []
	for line in guilds_page:
		if "450px" in line:
			page = line[line.index("page"): - 11]
			page = page[page.index("_") + 1:]
			banner = line[line.index("p"):line.index("|4")]
			guilds.append((page, banner))

	for guild, banner in guilds:  # , баннер -- костыль
		page = vkCap(
			api.pages.get,
			page_id=guild, group_id=group_id, need_source=1)

		page = page['source'].splitlines()
		for index, line in enumerate(page):
			if "nopadding;noborder;nolink" in line:
				logo = line[line.index("p"):line.index("|3")]

			elif "Глава" in line:
				head = re.findall(r"(id[0-9]+)+", line)
				head = (h[2:] for h in head)
				head = " ".join(head)

			elif "главы гильдии" in line:
				vice = re.findall(r"(id[0-9]+)+", line)
				vice = (v[2:] for v in vice)
				vice = " ".join(vice)

			elif "Требования" in line:
				r = page[index + 1]
				r = r[r.index(">") + 1:]
				requirements = r

			elif "'''Немного" in line:
				about = page[index + 1]
				about = about[about.index(">") + 1:]

			elif "|+" in line:
				guild_name = line[line.index("'''") + 3:-3]

			elif "выигранных" in line:
				wins = page[index + 1]
				wins = wins[2:]

			elif "проигранных" in line:
				loses = page[index + 1]
				loses = loses[2:]

		database.createGuild(
			name=guild_name, page=guild, logo=logo,
			banner=banner, head=head,
			vice=vice, requirements=requirements,
			about=about, wins=wins, loses=loses)

	genPlayers(guilds)
	database.rewrite()


def genPlayers(guilds):
	all_avatars = database.find("avatars").iter("avatar")
	for guild, banner in guilds:
		page = vkCap(api.pages.get,
			page_id=guild, group_id=group_id, need_source=1)
		page = page['source'].splitlines()
		for index, line in enumerate(page):
			if "|+" in line:
				g_name = line[line.index("'''") + 3:-3]
				g_element = database.getByField(kind="guilds", field="name", value=g_name)
				g_id = g_element.find("id").text

			elif "|-" in line:
				for i in range(1, 6):
					if "|-" in page[index + i]:
						row_num = i
						break

			elif ">[[id" in line:
				l = line
				player = l[l.index("[[") + 2:l.index("]]")]
				player = player.split("|")
				p_id = player[0][2:]
				p_name = player[1]
				avatar = page[index + row_num]
				avatar = avatar[avatar.index("p"):avatar.index("|12")]
				avatar = database.getByField(kind="avatars", field="link", value=avatar)
				avatar = avatar.find("id").text
				database.createPlayer(id=p_id, name=p_name, avatar=avatar, guild=g_id)


def genAvatars():
	if database.find("avatars") is not None:
		guilds_element = database.find("avatars")
		database.contents.remove(guilds_element)
	guilds = ET.SubElement(database.contents, "avatars")
	guilds_page = api.pages.get(
		page_id=51595629, group_id=group_id, need_source=1)
	guilds_page = guilds_page['source'].splitlines()
	for line in guilds_page:
		if "photo" in line:
			link = line[12:line.index("120px") - 1]
			database.createAvatar(link)
	database.rewrite()


if __name__ == "__main__":
	genAvatars()
	# genChallenges()
	# genGuilds()
