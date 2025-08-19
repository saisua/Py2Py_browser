import asyncio
import logging

from signal_protocol import state

from config import logger

from encryption.utils.load_encryption_keys import _load_encryption_keys
from encryption.generate_empty_store import generate_empty_store
from encryption.add_bundle_to_store import add_bundle_to_store

from p2p.utils.addr_to_str import addr_to_str


async def generate_peer_store(session_maker, sid, own_sid=None):
    (
        (
            addr,
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp
        ),
        store
    ) = await asyncio.gather(
        _load_encryption_keys(session_maker, sid),
        generate_empty_store(
            session_maker,
            own_sid,
            process_bundle=True
        )
    )

    target_addr_ip, target_addr_port = addr_to_str(addr)
    target_addr_str = f"{target_addr_ip}:{target_addr_port}"

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Generating peer store for {target_addr_str}")

    target_protocol_address = add_bundle_to_store(
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
        bundle_address=target_addr_str,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Generated peer store for {target_addr_str}")

    return store, target_protocol_address
