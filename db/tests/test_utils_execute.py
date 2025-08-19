import unittest
from unittest.mock import AsyncMock, patch
from db.utils.execute import _session_execute


class TestUtilsExecute(unittest.TestCase):
    @patch('db.utils.execute.async_sessionmaker')
    async def test_session_execute(self, mock_session_maker):
        mock_session = AsyncMock()
        mock_session_maker.return_value = mock_session

        await _session_execute(
            mock_session_maker,
            "SELECT 1",
            commit=True,
            fetch=True
        )
        self.assertTrue(mock_session.begin.called)
