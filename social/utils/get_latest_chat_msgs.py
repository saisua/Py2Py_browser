import os
import logging

from config import chat_dir


def get_latest_chat_msgs(
        chat_hash: str,
        first_message: str | None = None,
        last_message: str | None = None,
) -> list[str]:
    messages = os.listdir(os.path.join(chat_dir, chat_hash))

    if first_message is not None:
        if last_message is not None:
            messages = list(filter(
                lambda msg: (
                    msg > first_message
                    and msg < last_message
                ),
                messages,
            ))
        else:
            messages = list(filter(lambda msg: msg > first_message, messages))
    elif last_message is not None:
        messages = list(filter(lambda msg: msg < last_message, messages))

    logging.debug(f"Messages: {messages}")

    return messages
