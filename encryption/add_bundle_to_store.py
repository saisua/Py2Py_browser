import logging

from signal_protocol import state, session, address

from config import logger

from p2p.utils.addr_to_str import addr_to_str

from encryption.utils.deserialize_identity_keypair import (
    _deserialize_identity_keypair
)
from encryption.utils.deserialize_keypair import _deserialize_keypair


def add_bundle_to_store(
    store,
    bundle_data: dict | state.PreKeyBundle,
    *,
    bundle_address: str | None = None,
):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Adding bundle to store")

    if isinstance(bundle_data, dict):
        bundle_address = bundle_data['address']
        registration_id = bundle_data['registration_id']
        pre_key_id = bundle_data['pre_key_id']
        pre_key_priv = bundle_data['pre_key']
        pre_key_pub = bundle_data['pre_key_pub']
        signed_pre_key_id = bundle_data['signed_pre_key_id']
        signed_pre_key_priv = bundle_data['signed_pre_key']
        signed_pre_key_pub = bundle_data['signed_pre_key_pub']
        identity_key_pair = bundle_data['identity_key']

        if isinstance(bundle_address, bytes):
            bundle_ip, bundle_port = addr_to_str(bundle_address)
            bundle_address = f"{bundle_ip}:{bundle_port}"

        protocol_address = address.ProtocolAddress(
            bundle_address,
            registration_id
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Created protocol address for {bundle_address}")

        identity_key_pair = _deserialize_identity_keypair(identity_key_pair)
        pre_key_pair = _deserialize_keypair(pre_key_pub, pre_key_priv)
        signed_pre_key_pair = _deserialize_keypair(
            signed_pre_key_pub,
            signed_pre_key_priv
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Deserialized keypairs for {bundle_address}")

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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Created pre key bundle for {bundle_address}")
    else:
        bundle = bundle_data
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Using pre-existing pre key bundle for {bundle_address}")

        assert isinstance(bundle_address, str) and bundle_address, \
            bundle_address

        protocol_address = address.ProtocolAddress(
            bundle_address,
            bundle.registration_id()
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Created protocol address for {bundle_address}")

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Processing pre key bundle for {bundle_address}")

    session.process_prekey_bundle(protocol_address, store, bundle)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Processed pre key bundle for {bundle_address}")

    return protocol_address
