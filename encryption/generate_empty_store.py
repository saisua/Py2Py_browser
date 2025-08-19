import logging

from signal_protocol import state, storage

from sqlalchemy import select

from config import (
    logger,
    PEERTYPE_MYSELF,
)

from db.models.peers import Peers

from encryption.utils.load_encryption_keys import _load_encryption_keys

from db.utils.execute import _session_execute


async def generate_empty_store(session_maker, sid=None):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generating empty store")

    if sid is None:
        sid = await _session_execute(
            session_maker,
            select(Peers.sid).where(
                Peers.type == PEERTYPE_MYSELF
            ).limit(1),
            scalar=True
        )

    (
        addr,
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp,
    ) = await _load_encryption_keys(session_maker, sid)

    store = storage.InMemSignalProtocolStore(
        identity_key_pair,
        registration_id
    )

    signed_prekey = state.SignedPreKeyRecord(
        signed_pre_key_id,
        timestamp,
        signed_pre_key_pair,
        identity_key_pair.private_key()
        .calculate_signature(signed_pre_key_pair.public_key().serialize())
    )
    store.save_signed_pre_key(signed_pre_key_id, signed_prekey)

    pre_key_record = state.PreKeyRecord(pre_key_id, pre_key_pair)
    store.save_pre_key(pre_key_id, pre_key_record)

    return store
