import logging

from signal_protocol import session_cipher

from config.debugging_config import DEBUG_DISABLE_ENCRYPTION

from encryption.generate_peer_store import generate_peer_store


async def decrypt_message(session_maker, encrypted_message, sid):
    logging.debug(f"Decrypting message from {sid}")

    if DEBUG_DISABLE_ENCRYPTION:
        return encrypted_message

    store, peer_address = await generate_peer_store(session_maker, sid)

    message = session_cipher.message_decrypt(
        store,
        peer_address,
        encrypted_message
    )

    logging.debug(f"Decrypted message ({len(message)} bytes)")
    return message
