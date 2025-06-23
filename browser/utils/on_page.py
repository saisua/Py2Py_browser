import logging
from functools import partial

from communication.communication_user import CommunicationUser

from browser.utils.on_framenavigated import on_framenavigated


def on_page(comm_user: CommunicationUser, page):
    logging.info(f"Page created: {page.url}")
    page.on("framenavigated", partial(on_framenavigated, comm_user))
