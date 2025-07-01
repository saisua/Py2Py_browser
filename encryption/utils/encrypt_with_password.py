import logging

from config import logger

from encryption.utils.fernet_from_password import fernet_from_password


def encrypt_with_password(bundle: bytes, password: str) -> bytes:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Encrypting bundle with fernet password")

    fernet = fernet_from_password(password)
    return fernet.encrypt(bundle)
