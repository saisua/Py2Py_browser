import os
import asyncio
# from datetime import datetime
import logging

# import bson

from sqlalchemy import (
	select,
	delete,
	update,
)

from config import (
    logger,
    peer_addr_dir,
    DEBUG_REMOVE_PREV_PEERS,
    PEERTYPE_MYSELF,
    # PEERTYPE_CLIENT,
    suffix,
)

from db.models.peers import Peers
from db.utils.add_all import _session_add_all
from db.utils.execute import _session_execute

from p2p.utils.addr_to_str import addr_to_str
from p2p.utils.addr_to_bytes import addr_to_bytes

from encryption.add_new_peer_bundle import add_new_peer_bundle


wrong_addr_trials = 0


async def add_peers(session_maker, first_run=False):
    if DEBUG_REMOVE_PREV_PEERS and first_run:
        if logger.isEnabledFor(logging.INFO):
            logger.info("Removing previous peers")

        await _session_execute(
            session_maker,
            delete(Peers).where(
                Peers.type != PEERTYPE_MYSELF,
            ),
            commit=True,
        )

    async with session_maker() as session:
        async with session.begin() as transaction:
            try:
                known_addrs = await _session_execute(
                    transaction,
                    select(Peers.address, Peers.type),
                    fetch=True,
                    many=True,
                )
            except Exception as e:
                logger.error("Error getting addresses")
                logger.exception(e)
                raise

            own_addr = None
            own_addr_str = None
            known_str_addrs = set()
            for addr, type in known_addrs:
                if type == PEERTYPE_MYSELF:
                    own_addr = addr
                    own_addr_str = ':'.join(map(str, addr_to_str(addr)))
                else:
                    known_str_addrs.add(':'.join(map(str, addr_to_str(addr))))

            if own_addr is None:
                logger.error("No own address found")
                raise Exception("No own address found")

            # print("#### known_addrs", known_str_addrs)

            new_peers = list()
            for peer_bundle_file in os.listdir(peer_addr_dir):
                addr, peer_suffix = peer_bundle_file.split('-', 1)

                logger.warning("addr: %s, own_addr: %s, peer_suffix: %s", addr, own_addr_str, peer_suffix)
                if addr == own_addr_str:
                    logger.debug("Skipping own bundle")
                    continue
                if peer_suffix == suffix:
                    global wrong_addr_trials

                    wrong_addr_trials += 1
                    if wrong_addr_trials > 100:
                        logger.warning("Updating own address (%s)", own_addr)
                        addr_bytes = addr_to_bytes(*map(int, addr.split(':')))
                        await _session_execute(
                            transaction,
                            update(Peers)
                            .where(Peers.type == PEERTYPE_MYSELF)
                            .values(address=addr_bytes),
                        )
                        own_addr = addr
                    elif wrong_addr_trials > 200:
                        raise Exception("Too many wrong address trials")
                    else:
                        logger.warning("Getting own address (%s)", own_addr)
                        own_addr = await _session_execute(
                            transaction,
                            select(Peers.address).where(
                                Peers.type == PEERTYPE_MYSELF,
                            ),
                            scalar=True,
                        )
                        logger.warning("Got own address (%s)", own_addr)
                    continue
                if addr in known_str_addrs:
                    logger.debug("Skipping known bundle %s", addr)
                    continue

                try:
                    with open(
                        os.path.join(
                            peer_addr_dir,
                            peer_bundle_file,
                        ),
                        "rb",
                    ) as f:
                        bundle_bson = f.read()
                except Exception as e:
                    logger.error(f"Error reading bundle {peer_bundle_file}")
                    logger.exception(e)
                    continue

                try:
                    new_peer = await add_new_peer_bundle(
                        transaction,
                        bundle_bson,
                        own_password="debug_password",
                        other_password="debug_password",
                        add_peer=False,
                    )

                    new_peers.append(new_peer)
                except Exception as e:
                    logger.error("Error adding peer %s", addr)
                    logger.exception(e)
                else:
                    logger.info("Found peer %s", addr)

            if len(new_peers):
                try:
                    await _session_add_all(transaction, new_peers)
                except Exception as e:
                    logger.error(e)
            elif logger.isEnabledFor(logging.DEBUG):
                logger.debug("No new peers to add")

    # for testing

    # from encryption.generate_empty_store import generate_empty_store
    # store = await generate_empty_store(session_maker, own_addr)

    # import bson
    # from encryption.generate_peer_bundle import _generate_peer_bundle
    # from encryption.add_bundle_to_store import add_bundle_to_store
    # if len(known_addrs) == 0:
    #     known_addrs = [*(p.address for p in new_peers)]

    # for peer_addr in known_addrs:
    #     bundle = await _generate_peer_bundle(session_maker, peer_addr)
    #     bundle = bson.loads(bundle)
    #     add_bundle_to_store(store, bundle)
    #     print(f"Added {peer_addr} bundle to store", flush=False)


async def add_peers_forever(session_maker, first_run=True):
    await add_peers(session_maker, first_run)
    await asyncio.sleep(1)

    for _ in range(60):
        await add_peers(session_maker)
        await asyncio.sleep(0.5)

    for _ in range(30):
        await add_peers(session_maker)
        await asyncio.sleep(1)

    while True:
        await add_peers(session_maker)
        await asyncio.sleep(5)
