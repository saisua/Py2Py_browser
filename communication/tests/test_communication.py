import unittest
from unittest.mock import MagicMock, patch
from multiprocessing import Manager
from communication.communication import Communication
from communication.concurrency_layers import ThreadLayer, MainThreadLayer
from communication.message import Message

class TestCommunication(unittest.TestCase):
    def setUp(self):
        self.comm = Communication()
        # Patch the BROADCAST constant for testing
        self.patcher = patch('config.social_config.BROADCAST', -1)
        self.mock_broadcast = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_add_user(self):
        user1 = self.comm.add_user(1, ThreadLayer(1))
        self.assertIn(1, self.comm.users)
        self.assertEqual(user1.id, 1)
        
        user2 = self.comm.add_user(2, MainThreadLayer())
        self.assertIn(2, self.comm.users)
        self.assertEqual(user2.id, 2)

    def test_send_message_to_user(self):
        user1 = self.comm.add_user(1, ThreadLayer(1))
        user2 = self.comm.add_user(2, ThreadLayer(2))
        
        # Mock the user's lock
        user1.lock = MagicMock()
        user1.lock.__enter__.return_value = None
        user1.lock.__exit__.return_value = None
        
        # Send message to user1
        self.comm.send_message(1, 1, 1, "test", ThreadLayer(3))
        messages = user1.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "test")
        
        # user2 should have no messages
        self.assertEqual(len(user2.get_messages()), 0)

    def test_broadcast_message(self):
        user1 = self.comm.add_user(1, ThreadLayer(1))
        user2 = self.comm.add_user(2, ThreadLayer(2))
        
        # Mock the users' locks
        user1.lock = MagicMock()
        user1.lock.__enter__.return_value = None
        user1.lock.__exit__.return_value = None
        user2.lock = MagicMock()
        user2.lock.__enter__.return_value = None
        user2.lock.__exit__.return_value = None
        
        # Broadcast message
        self.comm.send_message(-1, 1, 1, "broadcast", ThreadLayer(3))
        
        # Both users should receive the message
        messages1 = user1.get_messages()
        messages2 = user2.get_messages()
        self.assertEqual(len(messages1), 1)
        self.assertEqual(len(messages2), 1)
        self.assertEqual(messages1[0].content, "broadcast")
        self.assertEqual(messages2[0].content, "broadcast")
