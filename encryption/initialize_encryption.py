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

from db.models.peers import Peers

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


async def initialize_encryption(session_maker, address: bytes):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Initializing encryption")

    async with session_maker() as session:
        async with session.begin() as transaction:
            # If exists peer in rowid 0, deserialize its data
            own_peer, own_addr_peer = await asyncio.gather(
                _session_execute(
                    transaction,
                    select(Peers.address).where(
                        Peers.type == PEERTYPE_MYSELF
                    ),
                    scalar=True,
                ),
                _session_execute(
                    transaction,
                    select(Peers.address, Peers.type).where(
                        Peers.address == address
                    ),
                    fetch=True,
                )
            )

            # print("#### own_peer", own_peer)
            # print("#### own_addr_peer", own_addr_peer)
            # print("#### address", address)

            if (
                own_addr_peer is not None
                and own_addr_peer[1] != PEERTYPE_MYSELF  # noqa: W503
            ):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Deleting existing peer with current address")

                await _session_execute(
                    transaction,
                    delete(Peers)
                    .where(Peers.address == address),
                )

            if own_peer is not None:
                if own_peer != address:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Updating existing peer")

                    existing_peer = await _session_execute(
                        transaction,
                        select(Peers).where(Peers.type == PEERTYPE_MYSELF),
                        fetch=True,
                        many=True,
                        expunge=True,
                    )
                    existing_peer_data = existing_peer[0][0].__dict__
                    # print("#### existing_peer", existing_peer)

                    await _session_execute(
                        transaction,
                        delete(Peers).where(Peers.type == PEERTYPE_MYSELF),
                    )

                    new_peer = Peers(
                        sid=existing_peer_data["sid"],
                        address=address,
                        checked_time=datetime.now(),
                        type=PEERTYPE_MYSELF,
                        identity_key=existing_peer_data["identity_key"],
                        registration_id=existing_peer_data["registration_id"],
                        signed_pre_key_id=existing_peer_data["signed_pre_key_id"],  # noqa: E501
                        signed_pre_key_pub=existing_peer_data["signed_pre_key_pub"],  # noqa: E501
                        signed_pre_key=existing_peer_data["signed_pre_key"],
                        pre_key_id=existing_peer_data["pre_key_id"],
                        pre_key_pub=existing_peer_data["pre_key_pub"],
                        pre_key=existing_peer_data["pre_key"],
                        timestamp=existing_peer_data["timestamp"],
                    )
                    await _session_add(transaction, new_peer)
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
                await _store_encryption_keys(
                    transaction,
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
