from datetime import datetime
import logging

import bson

from encryption.add_bundle_to_store import add_bundle_to_store
from encryption.utils.decrypt_with_password import decrypt_with_password

from db.peers import Peers
from db.utils.add import _session_add


async def add_new_peer_bundle(
        session_maker,
        peer_bundle: bytes,
        store,
        *,
        own_password: str,
        other_password: str,
):
    logging.debug("Adding new peer bundle")

    now = datetime.now()

    own_decrypted_bundle = decrypt_with_password(
        peer_bundle,
        own_password,
    )
    decrypted_bundle = decrypt_with_password(
        own_decrypted_bundle,
        other_password,
    )
    deserialized_bundle = bson.loads(decrypted_bundle)

    new_peer = Peers(
        **deserialized_bundle,
        checked_time=now,
    )

    await _session_add(session_maker, new_peer)

    add_bundle_to_store(store, deserialized_bundle)
