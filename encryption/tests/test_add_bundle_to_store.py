from datetime import datetime
import unittest

import bson

import encryption.tests.setup  # type: ignore  # noqa: F401

from encryption.tests.conftest import addr1, addr2

from config import PEERTYPE_MYSELF, PEERTYPE_CLIENT

from db import session_maker
from db.models.peers import Peers
from db.utils.add import _session_add
from db.utils.execute import _session_execute

from p2p.utils.get_peer_sid import get_peer_sid
from encryption.generate_empty_store import generate_empty_store
from encryption.generate_peer_bundle import _generate_peer_bundle
from encryption.add_bundle_to_store import add_bundle_to_store
from encryption.tests.test_initialize_encryption import TestInitializeEncryption


class TestAddBundleToStore(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Run the required test first
        suite = unittest.TestLoader().loadTestsFromTestCase(TestInitializeEncryption)
        unittest.TextTestRunner(verbosity=2).run(suite)

    async def test_add_bundle_to_store(self):
        await _session_execute(
            session_maker,
            Peers.__table__.delete().where(
                Peers.address == addr2
            ),
            commit=True,
        )

        sid1 = await get_peer_sid(session_maker, addr1)
        assert sid1 is not None
        assert isinstance(sid1, int)
        assert sid1 > 0

        store = await generate_empty_store(session_maker, sid1)
        self.assertIsNotNone(store)

        bundle = await _generate_peer_bundle(session_maker, addr2)
        self.assertIsNotNone(bundle)
        self.assertIsInstance(bundle, bytes)
        self.assertGreater(len(bundle), 0)

        bundle_data = bson.loads(bundle)
        self.assertIsInstance(bundle_data, dict)
        self.assertIn('address', bundle_data)
        self.assertIn('type', bundle_data)
        self.assertIn('identity_key', bundle_data)
        self.assertIn('registration_id', bundle_data)
        self.assertIn('pre_key_id', bundle_data)
        self.assertIn('pre_key', bundle_data)
        self.assertIn('pre_key_pub', bundle_data)
        self.assertIn('signed_pre_key_id', bundle_data)
        self.assertIn('signed_pre_key', bundle_data)
        self.assertIn('signed_pre_key_pub', bundle_data)
        self.assertIn('timestamp', bundle_data)
        self.assertIn('sid', bundle_data)

        bd_type = bundle_data.get('type')
        if bd_type is None or bd_type == PEERTYPE_MYSELF:
            bundle_data['type'] = PEERTYPE_CLIENT

            await _session_add(
                session_maker,
                Peers(
                    checked_time=datetime.now(),
                    **bundle_data,
                )
            )

        add_bundle_to_store(store, bundle_data)
