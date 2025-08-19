import unittest
from datetime import datetime
from db.models.group_members import GroupMembers


class TestGroupMembers(unittest.TestCase):
    def test_group_members_model(self):
        member = GroupMembers(
            group_hash='test_group',
            member_hash='test_member',
            checked_time=datetime.now()
        )
        self.assertEqual(member.group_hash, 'test_group')
        self.assertEqual(member.member_hash, 'test_member')
