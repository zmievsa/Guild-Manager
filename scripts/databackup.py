#!/usr/bin/env python3

from time import strftime
from shutil import copyfile


def backup():
	title = strftime("database_backups/%d.%m.%Y.xml")
	path = "../Data/"
	copyfile(path + "database.xml", path + title)


if __name__ == "__main__":
	backup()
