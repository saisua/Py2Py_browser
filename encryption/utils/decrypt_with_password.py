import logging

from config import logger

from encryption.utils.fernet_from_password import fernet_from_password


def decrypt_with_password(bundle: bytes, password: str) -> bytes:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Decrypting bundle with fernet password")

    fernet = fernet_from_password(password)
    return fernet.decrypt(bundle)
