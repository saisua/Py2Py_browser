from typing import Any
from multiprocessing.synchronize import Lock as Lock_t
from sortedcontainers import SortedList
import logging

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
        logging.info(f'Created comm user {user_id}')
        self.id = user_id
        self.comm = comm
        self.messages = SortedList()
        self.layer = user_concurrency_layer
        self.lock = lock

    def recv_message(
        self,
        priority: int,
        topic: int,
        content: Any,
        layer: concurrency_layer_t
    ):
        logging.debug(f'Received message p={priority} id={self.id} {content}')
        if self.layer.must_lock(layer):
            with self.lock:
                self.messages.add(Message(priority, topic, content, layer))
        else:
            self.messages.add(Message(priority, topic, content, layer))

    def send_message(
        self,
        user_id: int,
        priority: int,
        topic: int,
        content: Any,
    ):
        self.comm.send_message(
            user_id,
            priority,
            topic,
            content,
            self.layer,
        )
