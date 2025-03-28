import logging

from config import USER_COLOR_RANGE, USER_COLOR_START


def get_user_hash_color(user: str) -> tuple[int, int, int, int]:
    user_hash = hash(user)

    logging.debug(f"User hash: {user_hash}")

    color = (
        (user_hash % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        ((user_hash >> 6) % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        ((user_hash >> 12) % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        1.0,
    )

    logging.debug(f"Color: {color}")

    return color
