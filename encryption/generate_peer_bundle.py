import bson
import random
import string
import logging

from sqlalchemy import select

from config import (
    logger,
    PEERTYPE_MYSELF,
    PEERTYPE_CLIENT,
)

from db.utils.execute import _session_execute
from db.models.peers import Peers

from encryption.utils.encrypt_with_password import encrypt_with_password


async def _generate_peer_bundle(
    session_maker,
    address: bytes | None = None,
):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generating peer bundle")

    if address is None:
        query = select(Peers).where(Peers.type == PEERTYPE_MYSELF).limit(1)
    else:
        query = select(Peers).where(Peers.address == address).limit(1)

    peer = await _session_execute(
        session_maker,
        query,
        scalar=True,
        expunge=True,
    )

    assert peer is not None

    if peer.type == PEERTYPE_MYSELF:
        peer_type = PEERTYPE_CLIENT
    else:
        peer_type = peer.type

    return bson.dumps({
        'address': peer.address,
        'type': peer_type,
        'identity_key': peer.identity_key,
        'registration_id': peer.registration_id,
        'pre_key_id': peer.pre_key_id,
        'pre_key': peer.pre_key,
        'pre_key_pub': peer.pre_key_pub,
        'signed_pre_key_id': peer.signed_pre_key_id,
        'signed_pre_key': peer.signed_pre_key,
        'signed_pre_key_pub': peer.signed_pre_key_pub,
        'timestamp': peer.timestamp,
        'sid': peer.sid,
    })


def _generate_random_password(length: int = 6) -> str:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generating random password")

    return ''.join(
        random.choices(
            string.digits + string.ascii_lowercase,
            k=length
        )
    )


async def generate_peer_encrypted_bundle(
        session_maker,
        address: bytes | None = None,
        *,
        own_password: str | None = None,
        other_password: str,
) -> tuple[bytes, str]:
    if own_password is None:
        own_password = _generate_random_password()

    bundle = await _generate_peer_bundle(session_maker, address)

    own_encrypted_bundle = encrypt_with_password(
        bundle,
        own_password,
    )
    other_encrypted_bundle = encrypt_with_password(
        own_encrypted_bundle,
        other_password,
    )

    return other_encrypted_bundle, own_password
