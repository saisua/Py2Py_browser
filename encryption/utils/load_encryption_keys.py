import logging

from sqlalchemy import select

from config import logger

from db.models.peers import Peers
from db.utils.execute import _session_execute

from encryption.utils.deserialize_identity_keypair import (
    _deserialize_identity_keypair
)
from encryption.utils.deserialize_keypair import _deserialize_keypair


async def _load_encryption_keys(session_maker, sid):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Loading encryption keys for {sid}")

    peer_data = await _session_execute(
        session_maker,
        select(Peers).where(Peers.sid == sid),
        scalar=True,
        expunge=True,
    )

    if peer_data is None:
        raise Exception(f"No peer data found for {sid}")

    addr = peer_data.address

    identity_key_pair = _deserialize_identity_keypair(peer_data.identity_key)

    registration_id = peer_data.registration_id

    signed_pre_key_id = peer_data.signed_pre_key_id

    signed_pre_key_pair = _deserialize_keypair(
        peer_data.signed_pre_key_pub,
        peer_data.signed_pre_key
    )
    pre_key_id = peer_data.pre_key_id
    pre_key_pair = _deserialize_keypair(
        peer_data.pre_key_pub,
        peer_data.pre_key
    )
    timestamp = peer_data.timestamp

    return (
        addr,
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp,
    )
