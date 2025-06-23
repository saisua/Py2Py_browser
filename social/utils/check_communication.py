import asyncio
import logging

from config import BROWSER_URL_CHANGE

from communication.communication_user import CommunicationUser


async def check_communication(
    comm_user: CommunicationUser,
    app: "App",  # type: ignore # noqa: F821
):
    while True:
        for message in comm_user.get_messages():
            topic = message.topic

            if topic == BROWSER_URL_CHANGE:
                url = message.content
                if url in app.menu.menu_items:
                    app.menu.add_item(url, app.menu._change_chat_callback(url))
                await app.chat.change_chat(url)
            else:
                logging.warning(f"Unknown message topic: {message.topic}")
        await asyncio.sleep(1)
