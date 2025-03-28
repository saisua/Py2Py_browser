import bson
import random
import string
import logging

from sqlalchemy import select

from config import PEERTYPE_MYSELF

from db.utils.execute import _session_execute
from db.peers import Peers

from encryption.utils.encrypt_with_password import encrypt_with_password


async def _generate_peer_bundle(session_maker, address):
    logging.debug("Generating peer bundle")

    own_peer = await _session_execute(
        session_maker,
        select(Peers).where(Peers.type == PEERTYPE_MYSELF).limit(1),
        scalar=True,
        expunge=True,
    )

    assert own_peer is not None

    return bson.dumps({
        'address': own_peer.address,
        'type': own_peer.type,
        'identity_key': own_peer.identity_key,
        'registration_id': own_peer.registration_id,
        'pre_key_id': own_peer.pre_key_id,
        'pre_key': own_peer.pre_key,
        'pre_key_pub': own_peer.pre_key_pub,
        'signed_pre_key_id': own_peer.signed_pre_key_id,
        'signed_pre_key': own_peer.signed_pre_key,
        'signed_pre_key_pub': own_peer.signed_pre_key_pub,
        'timestamp': own_peer.timestamp,
        'sid': own_peer.sid,
    })


def _generate_random_password(length: int = 6) -> str:
    logging.debug("Generating random password")

    return ''.join(
        random.choices(
            string.digits + string.ascii_lowercase,
            k=length
        )
    )


async def generate_peer_encrypted_bundle(
        session_maker,
        address,
        *,
        own_password: str | None = None,
        other_password: str,
) -> bytes:
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

    return other_encrypted_bundle
