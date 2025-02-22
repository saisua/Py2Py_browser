from signal_protocol import state


def bundle_from_dict(bundle_dict: dict):
    """
        'identity_key': own_peer.identity_key,
        'registration_id': own_peer.registration_id,
        'pre_key_id': own_peer.pre_key_id,
        'pre_key': own_peer.pre_key,
        'pre_key_pub': own_peer.pre_key_pub,
        'signed_pre_key_id': own_peer.signed_pre_key_id,
        'signed_pre_key': own_peer.signed_pre_key,
        'signed_pre_key_pub': own_peer.signed_pre_key_pub,
        'timestamp': own_peer.timestamp,
    """
    raise NotImplementedError
    return state.PreKeyBundle(
        bundle_dict['registration_id'],
        1,
        bundle_dict['pre_key_id'],
    )
