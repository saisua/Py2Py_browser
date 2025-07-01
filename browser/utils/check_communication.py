import asyncio
import logging

from config import (
    logger,
    CLOSE,
)

from communication.communication_user import CommunicationUser


async def check_communication(
    comm_user: CommunicationUser,
    browser: "Browser",  # type: ignore # noqa: F821
):
    while True:
        messages = comm_user.get_messages()

        # if len(messages) != 0:
        #     print("social messages", messages)

        for message in messages:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Communication message: {message}")
            topic = message.topic

            if topic == CLOSE:
                if logger.isEnabledFor(logging.INFO):
                    logger.info("Closing browser")
                await browser.close()
                return
            elif logger.isEnabledFor(logging.WARNING):
                logger.warning(f"Unknown message topic: {message.topic}")
        await asyncio.sleep(1)
