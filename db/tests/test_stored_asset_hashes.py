import unittest
from datetime import datetime
from db.models.stored_asset_hashes import StoredAssetHashes


class TestStoredAssetHashes(unittest.TestCase):
    def test_stored_asset_hashes_model(self):
        hash_record = StoredAssetHashes(
            hash='test_hash',
            id=1,
            part=1,
            stored_dt=datetime.now()
        )
        self.assertEqual(hash_record.hash, 'test_hash')
        self.assertEqual(hash_record.id, 1)
