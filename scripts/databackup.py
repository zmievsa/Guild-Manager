#!/usr/bin/env python3

from lib.errors import ErrorManager
from lib.config import data_path
from shutil import copyfile
from time import strftime


def backup():
	title = strftime("database_backups/%d.%m.%Y.xml")
	copyfile(data_path + "database.xml", data_path + title)


if __name__ == "__main__":
	with ErrorManager("backup"):
		backup()
