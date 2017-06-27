from lib.commands import database
from lxml import etree as XML

guilds = database.find("guilds").iterchildren()
for guild in guilds:
	element = XML.SubElement(guild, "achi")
	element.text = ""

database.rewrite()