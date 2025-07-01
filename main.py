import asyncio
import os
import logging

from config import (
    logger,
    data_dir,
    hashes_dir,
    UPLOAD_FILES,
    DEBUG_PURGE_DATA,
    BROWSER_ID,
    SERVER_ID,
    SOCIAL_ID,
)

if DEBUG_PURGE_DATA:
    from debugging.purge_data import purge_data
    purge_data()

# noqa: E402

from db import session_maker, engine

from communication.communication import Communication
from communication.concurrency_layers import MainThreadLayer
from communication.concurrency_layers import ThreadLayer

from p2p.server import AsyncBsonServer

from browser.run_browser import run_browser

from social.run_social import SocialApp
from file_upload.upload_files import upload_files


# if DEBUG_ADD_PEERS:
#     from debugging.add_peers import add_peers
#     from debugging.add_groups import add_groups

#     add_peers(session_maker)
#     if DEBUG_ADD_GROUPS:
#         add_groups(session_maker)


async def main():
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(hashes_dir, exist_ok=True)

    comm = Communication()

    server_user = comm.add_user(SERVER_ID, ThreadLayer(1))
    server = AsyncBsonServer(session_maker, server_user)
    server.start()

    social_user = comm.add_user(SOCIAL_ID, MainThreadLayer())
    app = SocialApp(session_maker, social_user)

    if UPLOAD_FILES:
        if logger.isEnabledFor(logging.INFO):
            logger.info("Uploading files")
        upload_files_task = asyncio.create_task(
            upload_files(session_maker)
        )
    else:
        upload_files_task = None

    browser_user = comm.add_user(BROWSER_ID, MainThreadLayer())
    try:
        await asyncio.gather(
            run_browser(session_maker, browser_user),
            app.async_run(),
        )
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        try:
            app.stop()
        except Exception:
            pass
        try:
            server.stop()
        except Exception:
            pass
        try:
            await engine.dispose()
        except Exception:
            pass

    if upload_files_task is not None:
        await upload_files_task


if __name__ == "__main__":
    asyncio.run(main())
