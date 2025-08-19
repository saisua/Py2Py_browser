import asyncio
import logging
import traceback
from sqlalchemy import select

from config import (
    logger,
    DEBUG_ADD_GROUPS,
    PEERTYPE_MYSELF,
    DEBUG_DISABLE_PEER_REQUESTS,
)

from utils.hash_str import _hash_str

from db.models.group_members import GroupMembers
from db.models.peers import Peers
from db.utils.execute import _session_execute

from p2p.requests.chat_request import ChatRequest

from files.social.store_msg_bytes_to_disk import store_msg_bytes_to_disk


async def request_chat_and_reload(
    chat_widget: "Chat",  # noqa: F821 # type: ignore
    chat_hash: str,
    first_message: str | None = None,
    last_message: str | None = None,
):
    try:
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Requesting chat {chat_hash}")

        if not DEBUG_DISABLE_PEER_REQUESTS:
            # Get all peers in the chat
            peers = await _session_execute(
                chat_widget.app._session_maker,
                select(Peers).where(
                    Peers.type != PEERTYPE_MYSELF
                )
                if not DEBUG_ADD_GROUPS else
                select(GroupMembers.member_hash).where(  # TODO: Add sid
                    GroupMembers.group_hash == chat_hash
                ).where(
                    GroupMembers.type != PEERTYPE_MYSELF
                ),
                scalar=True,
                many=True,
                expunge=True,
            )

            if logger.isEnabledFor(logging.INFO):
                logger.info(f"Found {len(peers)} peers in chat {chat_hash}")

            if len(peers) != 0:
                own_sid = await _session_execute(
                    chat_widget.app._session_maker,
                    select(Peers.sid).where(
                        Peers.type == PEERTYPE_MYSELF
                    ),
                    scalar=True,
                )

            chat_request_coros = []
            for peer in peers:
                if logger.isEnabledFor(logging.INFO):
                    logger.info(f"Sending chat request to {peer}")
                chat_request_coros.append(
                    ChatRequest.send(
                        chat_widget.app._session_maker,
                        peer.address,
                        peer.sid,
                        chat_hash,
                        first_message,
                        last_message,
                        own_sid=own_sid,
                    )
                )

            chat_responses = await asyncio.gather(*chat_request_coros)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Received {len(chat_responses)} chat responses")

            chat_store_coros = []
            for res in chat_responses:
                if res is None or res.get('status') != 0:
                    logging.error(f" Error receiving chat response: {res}")
                    continue

                data = res.get('data')

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f" Received {len(data)} messages")

                for msg_hash, msg in data.items():
                    chat_store_coros.append(
                        store_msg_bytes_to_disk(
                            msg,
                            msg_hash,
                            chat_hash=chat_hash,
                            compress=False,
                        )
                    )

            if len(chat_store_coros) != 0:
                await asyncio.gather(*chat_store_coros)

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Stored {len(chat_store_coros)} messages")

                if _hash_str(chat_widget._chat) == chat_hash:
                    await chat_widget.reload_chat(request=False)
    except Exception:
        logging.error(traceback.format_exc())
        raise
