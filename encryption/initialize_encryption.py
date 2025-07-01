import random
from datetime import datetime
import asyncio
import logging

from sqlalchemy import select, update, delete

from signal_protocol import curve, identity_key

from config import (
    logger,
    PEERTYPE_MYSELF,
)

from db.peers import Peers

from db.utils.execute import _session_execute
from db.utils.add import _session_add


def _generate_encryption_keys():
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generating encryption keys")

    identity_key_pair = identity_key.IdentityKeyPair.generate()
    registration_id = random.randint(1, 16384)
    signed_pre_key_id = random.randint(1, 1000)
    signed_pre_key_pair = curve.KeyPair.generate()
    pre_key_id = random.randint(1, 1000)
    pre_key_pair = curve.KeyPair.generate()
    timestamp = 0
    sid = random.randint(1, 2 ** 32 - 1)
    return (
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp,
        sid,
    )


async def _store_encryption_keys(
    session_maker,
    address,
    identity_key_pair,
    registration_id,
    signed_pre_key_id,
    signed_pre_key_pair,
    pre_key_id,
    pre_key_pair,
    timestamp,
    sid
) -> None:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Storing encryption keys in peer")

    new_own_peer = Peers(
        address=address,
        checked_time=datetime.now(),
        type=PEERTYPE_MYSELF,
        identity_key=identity_key_pair.serialize(),
        registration_id=registration_id,
        signed_pre_key_id=signed_pre_key_id,
        signed_pre_key_pub=signed_pre_key_pair.public_key().serialize(),
        signed_pre_key=signed_pre_key_pair.private_key().serialize(),
        pre_key_id=pre_key_id,
        pre_key_pub=pre_key_pair.public_key().serialize(),
        pre_key=pre_key_pair.private_key().serialize(),
        timestamp=timestamp,
        sid=sid,
    )
    await _session_add(session_maker, new_own_peer)


async def initialize_encryption(session_maker, address):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Initializing encryption")

    # If exists peer in rowid 0, deserialize its data
    own_peer, own_addr_peer = await asyncio.gather(
        _session_execute(
            session_maker,
            select(Peers.address).where(
                Peers.type == PEERTYPE_MYSELF
            ),
            scalar=True,
        ),
        _session_execute(
            session_maker,
            select(Peers.address, Peers.type).where(
                Peers.address == address
            ),
            scalar=True,
        )
    )

    init_coros = []

    if own_addr_peer is not None and own_addr_peer[1] != PEERTYPE_MYSELF:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Deleting existing peer with current address")

        init_coros.append(
            _session_execute(
                session_maker,
                delete(Peers)
                .where(Peers.address == address),
                commit=True,
            )
        )

    if own_peer is not None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Updating existing peer")

        await asyncio.gather(*init_coros)
        init_coros.clear()

        init_coros.append(
            _session_execute(
                session_maker,
                update(Peers)
                .where(Peers.type == PEERTYPE_MYSELF)
                .values(
                    address=address,
                    checked_time=datetime.now()
                ),
                commit=True,
            )
        )
    else:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Generating new peer")

        (
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp,
            sid
        ) = _generate_encryption_keys()
        init_coros.append(
            _store_encryption_keys(
                session_maker,
                address,
                identity_key_pair,
                registration_id,
                signed_pre_key_id,
                signed_pre_key_pair,
                pre_key_id,
                pre_key_pair,
                timestamp,
                sid
            )
        )

    await asyncio.gather(*init_coros)
