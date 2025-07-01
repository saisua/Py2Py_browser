from enum import IntEnum, auto
import os

from config.global_config import suffix

USER_COLOR_START = os.getenv(
	"P2Py_SOCIAL_USER_COLOR_START",
	128
)
USER_COLOR_RANGE = os.getenv(
	"P2Py_SOCIAL_USER_COLOR_RANGE",
	32
)

MAX_CHAT_BUTTON_LENGTH = os.getenv(
	"P2Py_SOCIAL_MAX_CHAT_BUTTON_LENGTH",
	25
)

ENABLE_KEYBOARD_LISTENER = os.getenv(
	"P2Py_SOCIAL_ENABLE_KEYBOARD_LISTENER",
	False
)

max_chat_msgs = os.getenv(
	"P2Py_SOCIAL_MAX_CHAT_MESSAGES",
	25
)

username = os.getenv(
	"P2Py_SOCIAL_USERNAME",
	f"User{suffix}"
)

chats = os.getenv(
	"P2Py_SOCIAL_CHATS",
	"ME"
).split(',')

default_chat = chats[0]


class SocialCommTopics(IntEnum):
	CLOSE = auto()
	BROWSER_URL_CHANGE = auto()


BROADCAST = -1


globals().update({
	topic_k: topic_v.value
	for topic_k, topic_v in SocialCommTopics.__members__.items()
})
