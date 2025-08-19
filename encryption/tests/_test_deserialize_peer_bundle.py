import unittest
from unittest.mock import patch, MagicMock
from encryption.generate_peer_bundle import generate_peer_bundle


class TestGeneratePeerBundle(unittest.TestCase):
    @patch('encryption.generate_peer_bundle.generate_identity_keypair')
    @patch('encryption.generate_peer_bundle.generate_keypair')
    @patch('encryption.generate_peer_bundle.sign')
    def test_generate_peer_bundle(self, mock_sign, mock_gen_key, mock_gen_identity):
        mock_gen_identity.return_value = {'public': 'ipub', 'private': 'ipriv'}
        mock_gen_key.return_value = {'public': 'pub', 'private': 'priv'}
        mock_sign.return_value = 'signature'

        result = generate_peer_bundle()
        self.assertEqual(result['identity_keypair']['public'], 'ipub')
        self.assertEqual(result['prekey']['public'], 'pub')
        self.assertEqual(result['signed_prekey']['public'], 'pub')
        self.assertEqual(result['signed_prekey']['signature'], 'signature')
