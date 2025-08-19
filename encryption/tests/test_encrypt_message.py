import unittest

import encryption.tests.setup  # type: ignore  # noqa: F401

from encryption.tests.conftest import addr1, addr2

from db import session_maker

from p2p.utils.get_peer_sid import get_peer_sid
from encryption.encrypt_message import encrypt_message
from encryption.decrypt_message import decrypt_message
from encryption.tests.test_add_new_peer_bundle import TestAddNewPeerBundle


class TestEncryptMessage(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Run the required test first
        suite = unittest.TestLoader()\
            .loadTestsFromTestCase(TestAddNewPeerBundle)
        unittest.TextTestRunner(verbosity=2).run(suite)

    async def test_encrypt_message(self):
        # sid1 = await get_user_addr_sid(session_maker, addr1)
        sid2 = await get_peer_sid(session_maker, addr2)
        assert sid2 is not None
        assert isinstance(sid2, int)
        assert sid2 > 0

        message = b'test_data'
        encrypted_result = await encrypt_message(
            session_maker,
            message,
            sid2
        )
        self.assertIsNotNone(encrypted_result)
        self.assertIsInstance(encrypted_result, bytes)
        self.assertGreater(len(encrypted_result), 0)
        self.assertNotEqual(encrypted_result, message)

        print(f"Encrypted result: {encrypted_result}")
        with open('./encryption/tests/message_encrypted.bin', 'wb+') as f:
            f.write(encrypted_result)

        with open('./encryption/tests/message.bin', 'wb+') as f:
            f.write(message)

        # decrypted_result = await decrypt_message(
        #     session_maker,
        #     encrypted_result,
        #     sid1
        # )
        # self.assertEqual(decrypted_result, message)
