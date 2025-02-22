import asyncio

from config import UPLOAD_FILES

from p2p.server import AsyncBsonServer

from db import session_maker

from utils.upload_files import upload_files


async def main():
    if UPLOAD_FILES:
        print("Uploading files", flush=False)
        upload_files_task = asyncio.create_task(
            upload_files(session_maker)
        )
        await upload_files_task
        upload_files_task = None
    else:
        upload_files_task = None

    server = AsyncBsonServer(session_maker)
    server.start()
    input('Press Enter to stop...\n')
    server.stop()

    if upload_files_task is not None:
        await upload_files_task


if __name__ == "__main__":
    asyncio.run(main())
