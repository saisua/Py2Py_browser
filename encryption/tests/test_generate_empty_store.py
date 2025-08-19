import unittest

import encryption.tests.setup  # type: ignore  # noqa: F401
from encryption.tests.conftest import addr1

from db import session_maker
from encryption.generate_empty_store import generate_empty_store
from p2p.utils.get_peer_sid import get_peer_sid


class TestGenerateEmptyStore(unittest.IsolatedAsyncioTestCase):
    async def test_generate_empty_store(self):
        sid1 = await get_peer_sid(session_maker, addr1)
        assert sid1 is not None
        assert isinstance(sid1, int)
        assert sid1 > 0

        store = await generate_empty_store(session_maker, sid1)
        self.assertIsNotNone(store)
