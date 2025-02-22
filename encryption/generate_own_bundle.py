import bson
import random
import string

from sqlalchemy import select

from db.peers import Peers

from encryption.utils.encrypt_with_password import encrypt_with_password


async def _generate_own_bundle(session_maker):
    own_peer = await session_maker.execute(
        select(Peers).where(Peers.ROWID == 1)
    ).scalar()

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
    })


def _generate_random_password(length: int = 6) -> str:
    return ''.join(
        random.choices(
            string.digits + string.ascii_lowercase,
            k=length
        )
    )


async def generate_encrypted_own_bundle(
        session_maker,
        *,
        own_password: str | None = None,
        other_password: str,
) -> bytes:
    if own_password is None:
        own_password = _generate_random_password()

    bundle = await _generate_own_bundle(session_maker)

    own_encrypted_bundle = encrypt_with_password(
        bundle,
        own_password,
    )
    other_encrypted_bundle = encrypt_with_password(
        own_encrypted_bundle,
        other_password,
    )

    return other_encrypted_bundle
