import os
import logging

from config import (
    logger,
    chat_dir,
)

from files.utils.read_bson import _read_bson


async def load_msg_from_disk(msg: str, chat: str):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Loading message from disk: {msg} in chat: {chat}")

    return await _read_bson(os.path.join(chat_dir, chat, msg))
