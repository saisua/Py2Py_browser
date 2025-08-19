import unittest
from unittest.mock import patch, MagicMock

from encryption.utils.encrypt_with_password import encrypt_with_password


class TestEncryptWithPassword(unittest.TestCase):
    @patch('encryption.utils.encrypt_with_password.fernet_from_password')
    def test_encrypt_with_password(self, mock_fernet):
        mock_cipher = MagicMock()
        mock_cipher.encrypt.return_value = b'encrypted'
        mock_fernet.return_value = mock_cipher

        result = encrypt_with_password(b'test', 'password')
        self.assertEqual(result, b'encrypted')
