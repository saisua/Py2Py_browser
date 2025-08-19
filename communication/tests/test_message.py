import unittest
from datetime import datetime
from communication.message import Message
from communication.concurrency_layers import ThreadLayer


class TestMessage(unittest.TestCase):
    def test_message_creation(self):
        layer = ThreadLayer(1)
        msg = Message(1, 2, 3, "test", layer)
        self.assertEqual(msg.objective, 1)
        self.assertEqual(msg.priority, 2)
        self.assertEqual(msg.topic, 3)
        self.assertEqual(msg.content, "test")
        self.assertEqual(msg.layer, layer)
        self.assertIsInstance(msg.timestamp, datetime)

    def test_message_comparison(self):
        layer = ThreadLayer(1)
        # Create messages with explicit timestamps for reliable comparison
        old_time = datetime(2020, 1, 1)
        new_time = datetime(2025, 1, 1)

        msg_high_priority = Message(1, 2, 1, "test", layer)
        msg_low_priority = Message(1, 1, 1, "test", layer)
        msg_old = Message(1, 1, 1, "test", layer)
        msg_old.timestamp = old_time
        msg_new = Message(1, 1, 1, "test", layer)
        msg_new.timestamp = new_time

        # Higher priority comes first
        self.assertGreater(msg_high_priority, msg_low_priority)
        # Same priority, newer timestamp comes first
        self.assertGreater(msg_old, msg_new)
        # Equal messages
        self.assertEqual(msg_new, msg_new)
