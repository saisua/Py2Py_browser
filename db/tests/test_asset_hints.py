import unittest
from db.models.asset_hints import AssetHints


class TestAssetHints(unittest.TestCase):
    def test_asset_hints_model(self):
        hint = AssetHints(
            hash='test_hash',
            part=1,
            address_from='test_address',
            num_parts=5
        )
        self.assertEqual(hint.hash, 'test_hash')
        self.assertEqual(hint.part, 1)
