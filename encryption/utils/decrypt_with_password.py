from encryption.utils.fernet_from_password import fernet_from_password


def decrypt_with_password(bundle: bytes, password: str) -> bytes:
    fernet = fernet_from_password(password)
    return fernet.decrypt(bundle)
