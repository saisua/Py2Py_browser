from typing import Any
from multiprocessing.synchronize import Lock as Lock_t
from sortedcontainers import SortedList
import logging

from config import logger

from communication.concurrency_layers import concurrency_layer_t
from communication.message import Message


class CommunicationUser:
    comm: 'Communication'  # noqa: F821 # type: ignore
    id: int
    messages: SortedList
    layer: concurrency_layer_t
    lock: Lock_t

    def __init__(
        self,
        comm: 'Communication',  # noqa: F821 # type: ignore
        user_id: int,
        user_concurrency_layer: concurrency_layer_t,
        lock: Lock_t,
    ):
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'Created comm user {user_id}')
        self.id = user_id
        self.comm = comm
        self.messages = SortedList()
        self.layer = user_concurrency_layer
        self.lock = lock

    def __repr__(self):
        return (
            'CommunicationUser('
            f'id={self.id}, '
            f'layer={self.layer}, '
            f'messages={self.messages})'
        )

    def recv_message(
        self,
        priority: int,
        topic: int,
        content: Any,
        layer: concurrency_layer_t
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f'Receiving message '
                f'from {self.id} "{topic}: {content}"'
            )

        self.messages.add(
            Message(
                self.id,
                priority,
                topic,
                content,
                layer
            )
        )

    def send_message(
        self,
        user_id: int,
        priority: int,
        topic: int,
        content: Any,
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f'Sending message p={priority} from '
                f'{self.id} {topic}: {content}'
            )
        self.comm.send_message(
            user_id,
            priority,
            topic,
            content,
            self.layer,
        )

    def get_messages(self, max_n: int = 100) -> list[Message]:
        self = self.update_self()

        if len(self.messages) == 0:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'No messages for {self.id} {self.messages}')
            return list()

        with self.lock:
            messages = self.messages.copy()

            if len(messages) > max_n:
                messages = messages[-max_n:]
                self.messages = messages[:-max_n]
            else:
                self.messages.clear()

            self.comm.users[self.id] = self

            return messages

    def update_self(self):
        return self.comm.users[self.id]
