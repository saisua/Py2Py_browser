import unittest

import encryption.tests.setup  # type: ignore  # noqa: F401
from encryption.tests.conftest import addr1

from db import session_maker

from encryption.initialize_encryption import initialize_encryption


class TestInitializeEncryption(unittest.IsolatedAsyncioTestCase):
    async def test_initialize_encryption(self):
        await initialize_encryption(session_maker, addr1)
