import unittest
from datetime import datetime
from db.models.peers import Peers


class TestPeers(unittest.TestCase):
    def test_peers_model(self):
        peer = Peers(
            address=b'test_address',
            checked_time=datetime.now(),
            type=1,
            identity_key=b'test_key',
            registration_id=1,
            pre_key_id=1,
            pre_key=b'test_pre_key',
            pre_key_pub=b'test_pre_key_pub',
            signed_pre_key_id=1,
            signed_pre_key=b'test_signed_key',
            signed_pre_key_pub=b'test_signed_key_pub',
            timestamp=123456789,
            sid=1
        )
        self.assertEqual(peer.address, b'test_address')
        self.assertEqual(peer.type, 1)
