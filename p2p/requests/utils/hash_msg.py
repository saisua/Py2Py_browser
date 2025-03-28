from datetime import datetime

from utils.hash_str import _hash_str


def _hash_msg(msg: dict) -> str:
    return f"{datetime.now().timestamp()}{_hash_str(msg['user'])}"
