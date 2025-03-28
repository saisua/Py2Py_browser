import os
import logging

from config import chat_dir

from files.utils.read_bson import _read_bson


async def load_msg_from_disk(msg: str, chat: str):
    logging.debug(f"Loading message from disk: {msg} in chat: {chat}")

    return await _read_bson(os.path.join(chat_dir, chat, msg))
