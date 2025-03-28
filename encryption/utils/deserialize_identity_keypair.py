from signal_protocol import identity_key


def _deserialize_identity_keypair(
    ik_bytes: bytes
) -> identity_key.IdentityKeyPair:
    return identity_key.IdentityKeyPair.from_bytes(ik_bytes)
