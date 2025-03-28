import hashlib


def _hash_str(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()
