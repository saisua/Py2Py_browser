import unittest
from unittest.mock import patch, MagicMock

from encryption.utils.decrypt_with_password import decrypt_with_password


class TestDecryptWithPassword(unittest.TestCase):
    @patch('encryption.utils.decrypt_with_password.fernet_from_password')
    def test_decrypt_with_password(self, mock_fernet):
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b'decrypted'
        mock_fernet.return_value = mock_cipher

        result = decrypt_with_password(b'encrypted', 'password')
        self.assertEqual(result, b'decrypted')