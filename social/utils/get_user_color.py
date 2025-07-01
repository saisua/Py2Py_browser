import logging

from config import (
    logger,
    USER_COLOR_RANGE,
    USER_COLOR_START,
)


def get_user_hash_color(user: str) -> tuple[int, int, int, int]:
    user_hash = hash(user)

    color = (
        (user_hash % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        ((user_hash >> 6) % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        ((user_hash >> 12) % USER_COLOR_RANGE + USER_COLOR_START) / 256,
        1.0,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"User hash: {user_hash}")
        logger.debug(f"Color: {color}")

    return color
