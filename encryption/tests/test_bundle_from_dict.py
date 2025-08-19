import unittest
from unittest.mock import patch, MagicMock

from encryption.utils.bundle_from_dict import bundle_from_dict


class TestBundleFromDict(unittest.TestCase):
    def test_bundle_from_dict(self):
        test_dict = {
            'identity_keypair': {'public': 'pub', 'private': 'priv'},
            'prekey': {'public': 'pub', 'private': 'priv'},
            'signed_prekey': {'public': 'pub', 'private': 'priv', 'signature': 'sig'}
        }
        result = bundle_from_dict(test_dict)
        self.assertEqual(result.identity_keypair.public, 'pub')
        self.assertEqual(result.prekey.public, 'pub')
        self.assertEqual(result.signed_prekey.public, 'pub')
