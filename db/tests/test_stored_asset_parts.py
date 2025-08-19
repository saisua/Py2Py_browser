import unittest
from datetime import datetime
from db.models.stored_asset_parts import StoredAssetParts


class TestStoredAssetParts(unittest.TestCase):
    def test_stored_asset_parts_model(self):
        part = StoredAssetParts(
            hash='test_hash',
            part=1,
            stored_dt=datetime.now()
        )
        self.assertEqual(part.hash, 'test_hash')
        self.assertEqual(part.part, 1)
