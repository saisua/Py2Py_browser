import unittest

import bson

from encryption.tests.conftest import addr2
import encryption.tests.setup  # type: ignore  # noqa: F401

from db import session_maker

from encryption.generate_peer_bundle import _generate_peer_bundle


class TestGeneratePeerBundle(unittest.IsolatedAsyncioTestCase):
    async def test_generate_peer_bundle(self):
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
