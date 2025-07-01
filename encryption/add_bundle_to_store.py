import logging

from signal_protocol import state, session, address

from config import logger

from encryption.utils.deserialize_identity_keypair import (
    _deserialize_identity_keypair
)
from encryption.utils.deserialize_keypair import _deserialize_keypair


def add_bundle_to_store(store, bundle_data: dict):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Adding bundle to store")

    bundle_address = bundle_data['address']
    registration_id = bundle_data['registration_id']
    pre_key_id = bundle_data['pre_key_id']
    pre_key_priv = bundle_data['pre_key']
    pre_key_pub = bundle_data['pre_key_pub']
    signed_pre_key_id = bundle_data['signed_pre_key_id']
    signed_pre_key_priv = bundle_data['signed_pre_key']
    signed_pre_key_pub = bundle_data['signed_pre_key_pub']
    identity_key_pair = bundle_data['identity_key']

    protocol_address = address.ProtocolAddress(
        bundle_address,
        registration_id
    )
    identity_key_pair = _deserialize_identity_keypair(identity_key_pair)
    pre_key_pair = _deserialize_keypair(pre_key_pub, pre_key_priv)
    signed_pre_key_pair = _deserialize_keypair(
        signed_pre_key_pub,
        signed_pre_key_priv
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
