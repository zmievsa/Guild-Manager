from lib import config
config.LOG_PATH = "tests/test_log.txt"
config.DATABASE_PATH = "tests/dummy_database"

from lib import commands
from lib.database import Database
from unittest.mock import MagicMock
mock_api = MagicMock()
commands.api = mock_api