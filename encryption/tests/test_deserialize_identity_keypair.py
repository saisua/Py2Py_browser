import unittest

from encryption.utils.deserialize_identity_keypair import deserialize_identity_keypair


class TestDeserializeIdentityKeypair(unittest.TestCase):
    def test_deserialize_identity_keypair(self):
        test_dict = {'public': 'pub', 'private': 'priv'}
        result = deserialize_identity_keypair(test_dict)
        self.assertEqual(result.public, 'pub')
        self.assertEqual(result.private, 'priv')
