from signal_protocol import curve


def _deserialize_keypair(
    pub_key_bytes: bytes,
    priv_key_bytes: bytes
) -> curve.KeyPair:
    return curve.KeyPair.from_public_and_private(
        pub_key_bytes,
        priv_key_bytes
    )
