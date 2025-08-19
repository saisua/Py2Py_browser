import asyncio
from datetime import datetime
import logging

from sqlalchemy import select

from utils.hash_str import _hash_str

from db.models.groups import Groups
from db.models.group_members import GroupMembers
from db.models.peers import Peers
from db.utils.execute import _session_execute
from db.utils.add_all import _session_add_all

from config import chats, logger


def add_groups(session_maker):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Adding groups")

    # Create session and get all peers
    peers = asyncio.run(_session_execute(session_maker, select(Peers.address)))

    # Create coroutines for adding groups and members
    new_groups = []
    new_members = []

    # Iterate through chats
    for chat in chats:
        # Hash the chat name
        chat_hash = _hash_str(chat)

        # Add group if it doesn't exist
        new_groups.append(
            Groups(
                hash=chat_hash,
                checked_time=datetime.now(),
                type=0,
            )
        )

        # Add all peers as members of this group
        for peer in peers:
            new_members.append(
                GroupMembers(
                    group_hash=chat_hash,
                    member_hash=peer.address,
                    checked_time=datetime.now(),
                )
            )

    try:
        asyncio.run(_session_add_all(session_maker, new_groups))
    except Exception as e:
        logger.error(e)

    try:
        asyncio.run(_session_add_all(session_maker, new_members))
    except Exception as e:
        logger.error(e)
