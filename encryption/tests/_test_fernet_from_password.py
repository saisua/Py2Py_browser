import unittest
from unittest.mock import patch
from encryption.utils.fernet_from_password import fernet_from_password


class TestFernetFromPassword(unittest.TestCase):
    @patch('encryption.utils.fernet_from_password.Fernet')
    def test_fernet_from_password(self, mock_fernet):
        fernet_from_password('test_password')
        mock_fernet.assert_called_once()