import unittest
from unittest.mock import AsyncMock, patch
from db.utils.add import _session_add


class TestUtilsAdd(unittest.TestCase):
    @patch('db.utils.add.async_sessionmaker')
    async def test_session_add(self, mock_session_maker):
        mock_session = AsyncMock()
        mock_session_maker.return_value = mock_session

        await _session_add(mock_session_maker, "test_item")
        mock_session.add.assert_called_with("test_item")
