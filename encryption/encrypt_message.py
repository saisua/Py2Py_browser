import logging

from signal_protocol import session_cipher

from config.debugging_config import DEBUG_DISABLE_ENCRYPTION

from encryption.generate_peer_store import generate_peer_store


async def encrypt_message(session_maker, message, sid):
    logging.debug(f"Encrypting message to {sid}")

    if DEBUG_DISABLE_ENCRYPTION:
        return message

    store, peer_address = await generate_peer_store(session_maker, sid)

    encrypted_message = session_cipher.message_encrypt(
        store,
        peer_address,
        message
    ).serialize()

    logging.debug(f"Encrypted message ({len(encrypted_message)} bytes)")

    return encrypted_message
