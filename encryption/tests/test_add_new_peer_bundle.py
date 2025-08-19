from datetime import datetime
import unittest

import encryption.tests.setup  # type: ignore  # noqa: F401

from config import PEERTYPE_CLIENT

from encryption.tests.conftest import addr1, addr2

from db import session_maker
from db.models.peers import Peers
from db.utils.add import _session_add
from db.utils.execute import _session_execute

from p2p.utils.get_peer_sid import get_peer_sid
from encryption.generate_empty_store import generate_empty_store
from encryption.generate_peer_bundle import generate_peer_encrypted_bundle
from encryption.initialize_encryption import _generate_encryption_keys
from encryption.add_new_peer_bundle import add_new_peer_bundle
from encryption.tests.test_initialize_encryption import TestInitializeEncryption


class TestAddNewPeerBundle(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Run the required test first
        suite = unittest.TestLoader().loadTestsFromTestCase(TestInitializeEncryption)
        unittest.TextTestRunner(verbosity=2).run(suite)

    async def test_add_new_peer_bundle(self):
        sid1 = await get_peer_sid(session_maker, addr1)
        assert sid1 is not None
        assert isinstance(sid1, int)
        assert sid1 > 0

        store = await generate_empty_store(session_maker, sid1)
        self.assertIsNotNone(store)

        (
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp,
            sid
        ) = _generate_encryption_keys()
        new_peer = Peers(
            address=addr2,
            checked_time=datetime.now(),
            type=PEERTYPE_CLIENT,
            identity_key=identity_key_pair.serialize(),
            registration_id=registration_id,
            signed_pre_key_id=signed_pre_key_id,
            signed_pre_key_pub=signed_pre_key_pair.public_key().serialize(),
            signed_pre_key=signed_pre_key_pair.private_key().serialize(),
            pre_key_id=pre_key_id,
            pre_key_pub=pre_key_pair.public_key().serialize(),
            pre_key=pre_key_pair.private_key().serialize(),
            timestamp=timestamp,
            sid=sid,
        )

        await _session_add(session_maker, new_peer)

        password1 = 'test_password1'
        password2 = 'test_password2'

        bundle, _ = await generate_peer_encrypted_bundle(
            session_maker,
            addr2,
            own_password=password2,
            other_password=password1,
        )
        self.assertIsNotNone(bundle)
        self.assertIsInstance(bundle, bytes)
        self.assertGreater(len(bundle), 0)

        await _session_execute(
            session_maker,
            Peers.__table__.delete().where(
                Peers.address == addr2
            ),
            commit=True,
        )

        await add_new_peer_bundle(
            session_maker,
            bundle,
            own_password=password1,
            other_password=password2,
        )
