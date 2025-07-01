import os
import logging

from config import (
    logger,
    chat_dir,
)

from utils.hash_str import _hash_str

from files.utils.store_bytes import _store_bytes


async def store_msg_bytes_to_disk(
    msg: bytes,
    msg_hash: str,
    *,
    chat: str | None = None,
    chat_hash: str | None = None,
    compress: bool = True,
):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Storing message bytes to disk: "
                     f"{msg_hash} in chat: {chat}")

    if chat_hash is None:
        if chat is None:
            raise ValueError("Chat or chat_hash must be provided")

        chat_hash = _hash_str(chat)

    await _store_bytes(
        os.path.join(chat_dir, chat_hash, msg_hash),
        msg,
        compress=compress,
    )
