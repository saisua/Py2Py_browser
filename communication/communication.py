from typing import Any
from multiprocessing import Manager

from communication.communication_user import CommunicationUser
from communication.concurrency_layers import concurrency_layer_t


class Communication:
    # We have some sort of dictionary that maps a user to a list of messages
    # which are sorted by priority and timestamp
    # When a user is created, it has to select wether they are in the
    # main thread, a child thread or a child process

    def __init__(self):
        self.manager = Manager()
        self.users = self.manager.dict()

    def __getstate__(self):
        return (
            self.users,
        )

    def __setstate__(self, state):
        self.users = state[0]

    def add_user(
        self,
        user_id: int,
        concurrency_layer: concurrency_layer_t
    ) -> CommunicationUser:
        new_user = CommunicationUser(
            self,
            user_id,
            concurrency_layer,
            self.manager.Lock(),
        )
        self.users[user_id] = new_user
        return new_user

    def send_message(
        self,
        user_id: int,
        priority: int,
        topic: int,
        content: Any,
        layer: concurrency_layer_t
    ):
        self.users[user_id].recv_message(
            priority,
            content,
            topic,
            layer,
        )
