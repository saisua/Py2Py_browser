import unittest
from unittest.mock import patch, MagicMock

from encryption.decrypt_message import decrypt_message


class TestDecryptMessage(unittest.TestCase):
    @patch('encryption.decrypt_message.Fernet')
    def test_decrypt_message(self, mock_fernet):
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b'decrypted_data'
        mock_fernet.return_value = mock_cipher

        result = decrypt_message(b'encrypted_data', 'test_password')
        self.assertEqual(result, b'decrypted_data')
        mock_cipher.decrypt.assert_called_with(b'encrypted_data')