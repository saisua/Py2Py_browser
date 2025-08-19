import unittest
from datetime import datetime
from db.models.assets import Assets


class TestAssets(unittest.TestCase):
    def test_assets_model(self):
        asset = Assets(
            hash='test_hash',
            domain_hash='test_domain',
            num_parts=5,
            created_time=datetime.now()
        )
        self.assertEqual(asset.hash, 'test_hash')
        self.assertEqual(asset.num_parts, 5)
