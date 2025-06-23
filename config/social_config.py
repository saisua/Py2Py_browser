from enum import IntEnum, auto

from config.global_config import suffix

USER_COLOR_START = 128
USER_COLOR_RANGE = 32

MAX_CHAT_BUTTON_LENGTH = 10

max_chat_msgs = 25

username = f"User{suffix}"

chats = [
    "test",
    "test2",
    "test3",
]

default_chat = chats[0]


class SocialCommTopics(IntEnum):
    BROWSER_URL_CHANGE = auto()


globals().update({
    topic_k: topic_v.value
    for topic_k, topic_v in SocialCommTopics.__members__.items()
})
