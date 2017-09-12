#!/usr/bin/env python3

from lib.errors import ErrorManager
from lib.config import data_folder
from shutil import copyfile
from time import strftime
from logging import getLogger

logger = getLogger("GM.backup_database")


def backup():
	logger.debug("Backing up database...")
	title = strftime("database_backups/%d.%m.%Y")
	copyfile(data_folder + "database", data_folder + title)


if __name__ == "__main__":
	with ErrorManager("backup"):
		backup()
