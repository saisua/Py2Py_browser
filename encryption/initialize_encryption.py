import random
from sqlalchemy import select

from signal_protocol import curve, identity_key, state, storage

from db.peers import Peers

from db.utils.execute import execute
from db.utils.add import _session_add


def _generate_encryption_keys():
    identity_key_pair = identity_key.IdentityKeyPair.generate()
    registration_id = random.randint(1, 16384)
    signed_pre_key_id = random.randint(1, 1000)
    signed_pre_key_pair = curve.KeyPair.generate()
    pre_key_id = random.randint(1, 1000)
    pre_key_pair = curve.KeyPair.generate()
    timestamp = 0
    return (
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp
    )


def _load_encryption_keys(own_peer):
    identity_key_pair = identity_key.IdentityKeyPair.from_bytes(
        own_peer.identity_key
    )
    registration_id = own_peer.registration_id
    signed_pre_key_id = own_peer.signed_pre_key_id
    signed_pre_key_pair = curve.KeyPair.from_public_and_private(
        own_peer.signed_pre_key_pub,
        own_peer.signed_pre_key
    )
    pre_key_id = own_peer.pre_key_id
    pre_key_pair = curve.KeyPair.from_public_and_private(
        own_peer.pre_key_pub,
        own_peer.pre_key
    )
    timestamp = own_peer.timestamp
    return (
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp
    )


async def _store_encryption_keys(
        session_maker,
        identity_key_pair,
        registration_id,
        signed_pre_key_id,
        signed_pre_key_pair,
        pre_key_id,
        pre_key_pair,
        timestamp
        ) -> None:
    new_own_peer = Peers(
        ROWID=0,
        identity_key=identity_key_pair.serialize(),
        registration_id=registration_id,
        signed_pre_key_id=signed_pre_key_id,
        signed_pre_key_pub=signed_pre_key_pair.public_key().serialize(),
        signed_pre_key=signed_pre_key_pair.private_key().serialize(),
        pre_key_id=pre_key_id,
        pre_key_pub=pre_key_pair.public_key().serialize(),
        pre_key=pre_key_pair.private_key().serialize(),
        timestamp=timestamp
    )
    await _session_add(session_maker, new_own_peer)


async def initialize_encryption(session_maker):
    # If exists peer in rowid 0, deserialize its data
    own_peer = await execute(
        session_maker,
        select(Peers).where(Peers.ROWID == 0)
    )
    own_peer_data = own_peer.scalar()

    if own_peer_data is not None:
        (
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp
        ) = _load_encryption_keys(own_peer_data)
    else:
        (
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp
        ) = _generate_encryption_keys()
        await _store_encryption_keys(
            session_maker,
            identity_key_pair,
            registration_id,
            signed_pre_key_id,
            signed_pre_key_pair,
            pre_key_id,
            pre_key_pair,
            timestamp
        )

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
