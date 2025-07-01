import os
import asyncio
from datetime import datetime
import logging

import bson

from sqlalchemy import select, delete

from config import (
    logger,
    peer_addr_dir,
    DEBUG_REMOVE_PREV_PEERS,
    PEERTYPE_MYSELF,
    PEERTYPE_CLIENT,
    suffix,
)

from db.peers import Peers
from db.utils.add_all import _session_add_all
from db.utils.execute import _session_execute

from p2p.utils.addr_to_str import addr_to_str
from p2p.utils.addr_to_bytes import addr_to_bytes

first_peers_removed = False


async def add_peers(session_maker):
    global first_peers_removed

    if DEBUG_REMOVE_PREV_PEERS and not first_peers_removed:
        first_peers_removed = True

        if logger.isEnabledFor(logging.INFO):
            logger.info("Removing previous peers")

        await _session_execute(
            session_maker,
            delete(Peers).where(
                Peers.type != PEERTYPE_MYSELF,
            ),
            commit=True,
        )

    known_addrs = await _session_execute(
        session_maker,
        select(Peers.address),
        scalar=True,
        many=True,
    )
    known_addrs = [
        ':'.join(map(str, addr_to_str(addr)))
        for addr in known_addrs
    ]

    new_peers = list()
    for peer_bundle_file in os.listdir(peer_addr_dir):
        addr, peer_suffix = peer_bundle_file.split('-', 1)
        if peer_suffix == suffix:
            continue
        if addr in known_addrs:
            continue

        with open(
            os.path.join(
                peer_addr_dir,
                peer_bundle_file,
            ),
            "rb",
        ) as f:
            bundle_bson = f.read()

        bundle_data = bson.loads(bundle_bson)

        if bundle_data.get('address') is None:
            addr, port = addr.rsplit(':', 1)
            bundle_data['address'] = addr_to_bytes(addr, port)

        bd_type = bundle_data.get('type')
        if bd_type is None or bd_type == PEERTYPE_MYSELF:
            bundle_data['type'] = PEERTYPE_CLIENT

        try:
            new_peers.append(
                Peers(
                    checked_time=datetime.now(),
                    **bundle_data,
                )
            )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Added peer {addr}")
        except Exception as e:
            logger.error(e)

    if len(new_peers):
        try:
            await _session_add_all(session_maker, new_peers)
        except Exception as e:
            logger.error(e)
    elif logger.isEnabledFor(logging.DEBUG):
        logger.debug("No new peers to add")

    # for testing

    # from encryption.generate_empty_store import generate_empty_store
    # store = await generate_empty_store(session_maker, known_addrs[0])

    # import bson
    # from encryption.generate_peer_bundle import _generate_peer_bundle
    # from encryption.add_bundle_to_store import add_bundle_to_store
    # if len(known_addrs) <= 1:
    #     known_addrs = [*known_addrs, *(p.address for p in new_peers)]

    # for peer_addr in known_addrs[1:]:
    #     bundle = await _generate_peer_bundle(session_maker, peer_addr)
    #     bundle = bson.loads(bundle)
    #     add_bundle_to_store(store, bundle)
    #     print(f"Added {peer_addr} bundle to store", flush=False)


async def add_peers_forever(session_maker):
    for _ in range(60):
        await add_peers(session_maker)
        await asyncio.sleep(0.5)

    for _ in range(30):
        await add_peers(session_maker)
        await asyncio.sleep(1)

    while True:
        await add_peers(session_maker)
        await asyncio.sleep(5)
