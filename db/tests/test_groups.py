import unittest
from datetime import datetime
from db.models.groups import Groups


class TestGroups(unittest.TestCase):
    def test_groups_model(self):
        group = Groups(
            hash='test_hash',
            checked_time=datetime.now(),
            type=1
        )
        self.assertEqual(group.hash, 'test_hash')
        self.assertEqual(group.type, 1)
