import unittest

from tests.util import mock_api, dummy_database
from topics.modules import guild_changes


class TopicTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		pass


class TestGuildChanges(TopicTestCase):
	pass


if __name__ == "__main__":
	unittest.main()