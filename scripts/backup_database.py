#!/usr/bin/env python3

from lib.errors import ErrorManager
from lib.config import data_folder
from shutil import copyfile
from time import strftime


def backup():
	title = strftime("database_backups/%d.%m.%Y.xml")
	copyfile(data_folder + "database.xml", data_folder + title)


if __name__ == "__main__":
	with ErrorManager("backup"):
		backup()
