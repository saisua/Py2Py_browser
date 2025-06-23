import logging

from config import (
    SOCIAL_ID,
    BROWSER_URL_CHANGE,
    DEBUG_DISABLE_COMMUNICATION,
)

from communication.communication_user import CommunicationUser


def on_framenavigated(comm_user: CommunicationUser, frame):
    logging.debug(f"Frame navigated: {frame.url}")
    if not DEBUG_DISABLE_COMMUNICATION:
        comm_user.send_message(
            SOCIAL_ID,
            0,
            BROWSER_URL_CHANGE,
            frame.url,
        )
