import base64
import logging

from config import logger

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

from config import static_salt


def fernet_from_password(password: str) -> Fernet:
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Generating Fernet encryption/decryption key from password"
        )

    key = base64.urlsafe_b64encode(
        PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=static_salt,
            iterations=1_000_000,
        ).derive(password.encode())
    )

    return Fernet(key)
