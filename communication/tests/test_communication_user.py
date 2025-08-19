import unittest
from unittest.mock import MagicMock, patch
from communication.communication_user import CommunicationUser
from communication.concurrency_layers import ThreadLayer


class TestCommunicationUser(unittest.TestCase):
    def setUp(self):
        self.comm_mock = MagicMock()
        self.user_id = 1
        self.layer = ThreadLayer(1)
        self.lock_mock = MagicMock()
        self.user = CommunicationUser(self.comm_mock, self.user_id, self.layer, self.lock_mock)

    def test_initialization(self):
        self.assertEqual(self.user.id, self.user_id)
        self.assertEqual(self.user.layer, self.layer)
        self.assertEqual(len(self.user.messages), 0)

    def test_recv_message(self):
        with patch('communication.message.datetime') as mock_datetime:
            mock_datetime.now.return_value = "2023-01-01"
            self.user.recv_message(1, 1, "test", self.layer)
            self.assertEqual(len(self.user.messages), 1)
            received_msg = self.user.messages[0]
            self.assertEqual(received_msg.content, "test")

    def test_send_message(self):
        self.user.send_message(2, 1, 1, "test")
        self.comm_mock.send_message.assert_called_once_with(2, 1, 1, "test", self.layer)

    def test_get_messages(self):
        # Test empty messages
        self.assertEqual(self.user.get_messages(), [])

        # Test with messages
        with patch('communication.message.datetime') as mock_datetime:
            mock_datetime.now.side_effect = ["2023-01-01", "2023-01-02"]
            self.user.recv_message(1, 1, "test1", self.layer)
            self.user.recv_message(1, 2, "test2", self.layer)

            # Mock the lock context manager
            self.lock_mock.__enter__.return_value = None
            self.lock_mock.__exit__.return_value = None

            messages = self.user.get_messages()
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0].content, "test1")
            self.assertEqual(messages[1].content, "test2")
            self.assertEqual(len(self.user.messages), 0)
