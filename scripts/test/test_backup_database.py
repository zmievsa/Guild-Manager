import unittest
from unittest.mock import patch
import backup_database
from lib import config


class StandardBackupTestCase(unittest.TestCase):
	""" Dummy test for learning """
	def testStandardBackup(self):
		with patch("shutil.copyfile") as copyfile:
			backup_database.copyfile = copyfile
			backup_database.backup()
			self.assertTrue(copyfile.called)


if __name__ == "__main__":
	unittest.__main__()
