import asyncio
import logging

from signal_protocol import state, session, address

from encryption.utils.load_encryption_keys import _load_encryption_keys
from encryption.generate_empty_store import generate_empty_store

from p2p.utils.addr_to_str import addr_to_str


async def generate_peer_store(session_maker, sid):
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
        generate_empty_store(session_maker, sid)
    )

    addr_str = ':'.join(map(str, addr_to_str(addr)))

    logging.debug(f"Generating peer store for {addr_str}")

    protocol_address = address.ProtocolAddress(
        addr_str,
        registration_id
    )

    bundle = state.PreKeyBundle(
        registration_id,
        store.get_local_registration_id(),
        pre_key_id,
        pre_key_pair.public_key(),
        signed_pre_key_id,
        signed_pre_key_pair.public_key(),
        identity_key_pair.private_key().calculate_signature(
            signed_pre_key_pair.public_key().serialize()
        ),
        identity_key_pair.identity_key()
    )

    # Alice processes Bob's pre-key bundle
    session.process_prekey_bundle(protocol_address, store, bundle)

    return store, protocol_address
