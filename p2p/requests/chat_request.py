import os
import asyncio
import logging

from config import chat_dir

from social.utils.get_latest_chat_msgs import get_latest_chat_msgs

from files.utils.read_bytes import _read_bytes

from p2p.utils.send_request import send_request

from p2p.requests.request import Request


class ChatRequest(Request):
    CODE = int("1000001", 2)

    def __init__(self, *args, **kwargs):
        pass

    async def handle(self, request, *args, **kwargs):
        logging.debug("Handling chat request")

        # origin_addr = request.
        chat_hash = request.get('chat_hash')

        if (
            not chat_hash
            or not os.path.exists(os.path.join(chat_dir, chat_hash))
        ):
            raise ValueError("Chat not found")

        first_message = request.get('first_message')
        last_message = request.get('last_message')

        msg_hashes = get_latest_chat_msgs(
            chat_hash,
            first_message=first_message,
            last_message=last_message,
        )

        logging.debug(f"Sending: {len(msg_hashes)} messages as response")

        # Get all messages whose name is greater than last_message
        message_data_coros = [
            _read_bytes(
                os.path.join(chat_dir, chat_hash, msg_hash),
                decompress=False,
            )
            for msg_hash in msg_hashes
        ]

        message_data = dict(zip(
            msg_hashes,
            await asyncio.gather(*message_data_coros)
        ))

        return {'status': 0, "data": message_data}

    @staticmethod
    async def send(
        session_maker,
        addr,
        sid,
        chat_hash,
        first_message: str | None = None,
        last_message: str | None = None,
    ):
        logging.debug(f"Sending chat request to {addr}")

        data = {
            'code': ChatRequest.CODE,
            'chat_hash': chat_hash,
        }

        if first_message is not None:
            data['first_message'] = first_message

        if last_message is not None:
            data['last_message'] = last_message

        return await send_request(session_maker, addr, sid, data)
