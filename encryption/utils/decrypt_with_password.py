import logging

from encryption.utils.fernet_from_password import fernet_from_password


def decrypt_with_password(bundle: bytes, password: str) -> bytes:
    logging.debug("Decrypting bundle with fernet password")

    fernet = fernet_from_password(password)
    return fernet.decrypt(bundle)
