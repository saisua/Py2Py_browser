import unittest

from encryption.utils.deserialize_keypair import deserialize_keypair


class TestDeserializeKeypair(unittest.TestCase):
    def test_deserialize_keypair(self):
        test_dict = {'public': 'pub', 'private': 'priv'}
        result = deserialize_keypair(test_dict)
        self.assertEqual(result.public, 'pub')
        self.assertEqual(result.private, 'priv')
