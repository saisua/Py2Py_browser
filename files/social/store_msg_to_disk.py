import os
import logging

from config import (
    logger,
    chat_dir,
)

from utils.hash_str import _hash_str

from files.utils.store_bson import _store_bson

from p2p.requests.utils.hash_msg import _hash_msg


async def store_msg_to_disk(
    msg: dict | bytes,
    msg_hash: str | None = None,
    *,
    chat: str | None = None,
    chat_hash: str | None = None,
    compress: bool = True,
):
    if msg_hash is None:
        msg_hash = _hash_msg(msg)

    if chat_hash is None:
        if chat is None:
            raise ValueError("Chat or chat_hash must be provided")

        chat_hash = _hash_str(chat)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Storing message to disk: {msg_hash} in chat: {chat}")

    await _store_bson(
        os.path.join(chat_dir, chat_hash, msg_hash),
        msg,
        compress=compress,
    )
