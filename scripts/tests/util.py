from lib import commands
from lib.database import Database
from unittest.mock import MagicMock

mock_api = MagicMock()
dummy_database = Database("tests/dummy_database")
commands.api = mock_api
commands.database = dummy_database