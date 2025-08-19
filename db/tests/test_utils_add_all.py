import unittest
from unittest.mock import AsyncMock, patch
from db.utils.add_all import _session_add_all


class TestUtilsAddAll(unittest.TestCase):
    @patch('db.utils.add_all.async_sessionmaker')
    async def test_session_add_all(self, mock_session_maker):
        mock_session = AsyncMock()
        mock_session_maker.return_value = mock_session

        await _session_add_all(mock_session_maker, ["item1", "item2"])
        mock_session.add_all.assert_called_with(["item1", "item2"])
