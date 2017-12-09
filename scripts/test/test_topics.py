import unittest
from unittest.mock import MagicMock
from topics.modules import guild_changes


mock_api = MagicMock()
# dummy_database = fixtures.DummyDatabase()


class TopicTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		pass


class TestGuildChanges(TopicTestCase):
	pass


if __name__ == "__main__":
	unittest.main()
		