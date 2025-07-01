import logging

from playwright.async_api import Frame

from config import (
    logger,
    SOCIAL_ID,
    BROWSER_URL_CHANGE,
    DEBUG_DISABLE_COMMUNICATION,
)

from communication.communication_user import CommunicationUser


def on_framenavigated(comm_user: CommunicationUser, frame: Frame):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Frame navigated: {frame.url}")

    if not DEBUG_DISABLE_COMMUNICATION:
        comm_user.send_message(
            SOCIAL_ID,
            0,
            BROWSER_URL_CHANGE,
            frame.url.split("?", 1)[0],
        )
