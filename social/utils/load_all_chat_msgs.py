import os
import asyncio
import logging
import traceback

from config import chat_dir, max_chat_msgs

from files.social.load_msg_from_disk import load_msg_from_disk

from social.utils.request_chat_and_reload import request_chat_and_reload


async def load_all_chat_msgs(
    chat_widget: "Chat",  # noqa: F821 # type: ignore
    chat_hash: str,
    *,
    reverse: bool = False,
    limit: int | None = max_chat_msgs,
    skip: int = 0,
    clear: bool = True,
    request: bool = True,
) -> None:
    try:
        logging.info(f"Loading all chat messages for {chat_hash}")

        chat_path = os.path.join(chat_dir, chat_hash)
        if os.path.exists(chat_path):
            messages = sorted(
                os.listdir(os.path.join(chat_dir, chat_hash)),
                reverse=reverse,
            )
        else:
            logging.info(
                f"Chat {chat_hash} does not exist, creating empty chat"
            )
            messages = []
            os.makedirs(chat_path)

        if len(messages) > skip + limit:
            last_message = messages[skip + limit]
        else:
            last_message = None

        if skip > 0 and len(messages) > skip:
            first_message = messages[skip - 1]
        else:
            first_message = None

        if request:
            chat_widget.app._task_refs.append(
                asyncio.create_task(
                    request_chat_and_reload(
                        chat_widget,
                        chat_hash,
                        first_message,
                        last_message,
                    )
                )
            )

        if len(messages):
            logging.info(
                f"Loading {len(messages[skip:skip + limit])}"
                "messages from disk"
            )

            msgs = await asyncio.gather(*(
                load_msg_from_disk(message, chat_hash)
                for message in messages[skip:skip + limit]
            ))

            await chat_widget.send_messages(
                msgs,
                chat_hash,
                reverse=reverse,
                clear=clear,
            )
    except Exception:
        logging.error(traceback.format_exc())
