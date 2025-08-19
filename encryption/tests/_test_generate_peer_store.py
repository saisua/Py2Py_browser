import unittest
from unittest.mock import patch, MagicMock

from encryption.generate_peer_store import generate_peer_store


class TestGeneratePeerStore(unittest.TestCase):
    @patch('encryption.generate_peer_store.os.makedirs')
    @patch('encryption.generate_peer_store.open')
    @patch('encryption.generate_peer_store.generate_peer_bundle')
    def test_generate_peer_store(self, mock_gen_bundle, mock_open, mock_makedirs):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_gen_bundle.return_value = {'key': 'value'}
        generate_peer_store()
        mock_makedirs.assert_called_once()
        mock_file.write.assert_called()
