import asyncio
import os

# TODO: Remove after testing
os.environ["P2Py_SUFFIX"] = "_2"

from config import (
    UPLOAD_FILES,
    SERVER_ID,
)

from communication.communication import Communication
from communication.concurrency_layers import ThreadLayer

from p2p.server import AsyncBsonServer

from db import session_maker

from file_upload.upload_files import upload_files


async def main():
    if UPLOAD_FILES:
        upload_files_task = asyncio.create_task(
            upload_files(session_maker)
        )
        await upload_files_task
        upload_files_task = None
    else:
        upload_files_task = None

    comm = Communication()

    server_user = comm.add_user(SERVER_ID, ThreadLayer(1))
    server = AsyncBsonServer(session_maker, server_user)
    server.start()
    input('Press Enter to stop...\n')
    server.stop()

    if upload_files_task is not None:
        await upload_files_task


if __name__ == "__main__":
    asyncio.run(main())
