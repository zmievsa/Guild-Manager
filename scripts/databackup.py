#!/usr/bin/env python3

from lib.errors import ErrorManager
from shutil import copyfile
from time import strftime


def backup():
	title = strftime("database_backups/%d.%m.%Y.xml")
	path = "../Data/"
	copyfile(path + "database.xml", path + title)


if __name__ == "__main__":
	with ErrorManager("backup"):
		backup()
