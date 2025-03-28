import logging

from encryption.utils.fernet_from_password import fernet_from_password


def encrypt_with_password(bundle: bytes, password: str) -> bytes:
    logging.debug("Encrypting bundle with fernet password")

    fernet = fernet_from_password(password)
    return fernet.encrypt(bundle)
