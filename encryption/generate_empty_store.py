import logging

from signal_protocol import state, storage

from sqlalchemy import select

from config import (
    logger,
    PEERTYPE_MYSELF,
)

from db.models.peers import Peers

from encryption.add_bundle_to_store import add_bundle_to_store
from encryption.utils.load_encryption_keys import _load_encryption_keys

from db.utils.execute import _session_execute

from p2p.utils.addr_to_str import addr_to_str


async def generate_empty_store(session_maker, sid=None, process_bundle=False):
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

    addr_str, addr_port = addr_to_str(addr)
    addr_str = f"{addr_str}:{addr_port}"

    store = storage.InMemSignalProtocolStore(
        identity_key_pair,
        registration_id
    )
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Created store for {addr_str}")

    signed_prekey = state.SignedPreKeyRecord(
        signed_pre_key_id,
        timestamp,
        signed_pre_key_pair,
        identity_key_pair.private_key()
        .calculate_signature(signed_pre_key_pair.public_key().serialize())
    )
    store.save_signed_pre_key(signed_pre_key_id, signed_prekey)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Saved signed pre key for {addr_str}")

    pre_key_record = state.PreKeyRecord(pre_key_id, pre_key_pair)
    store.save_pre_key(pre_key_id, pre_key_record)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Saved pre key for {addr_str}")

    if process_bundle:
        add_bundle_to_store(
            store,
            state.PreKeyBundle(
                registration_id,
                registration_id,
                pre_key_id,
                pre_key_pair.public_key(),
                signed_pre_key_id,
                signed_pre_key_pair.public_key(),
                identity_key_pair.private_key().calculate_signature(
                    signed_pre_key_pair.public_key().serialize()
                ),
                identity_key_pair.identity_key()
            ),
            bundle_address=addr_str,
        )

    return store
