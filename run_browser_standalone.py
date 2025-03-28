import asyncio
import os

from config import (
    data_dir,
    hashes_dir,
    UPLOAD_FILES,
    DEBUG_PURGE_DATA,
    BROWSER_ID,
)

if DEBUG_PURGE_DATA:
    from debugging.purge_data import purge_data
    purge_data()

from db import session_maker, engine

from communication.communication import Communication
from communication.concurrency_layers import MainThreadLayer

from browser.run_browser import run_browser
from utils.upload_files import upload_files


async def main():
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(hashes_dir, exist_ok=True)

    comm = Communication()

    if UPLOAD_FILES:
        print("Uploading files", flush=False)
        upload_files_task = asyncio.create_task(
            upload_files(session_maker)
        )
    else:
        upload_files_task = None

    browser_user = comm.add_user(BROWSER_ID, MainThreadLayer())
    try:
        await run_browser(session_maker, browser_user)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        await engine.dispose()

    if upload_files_task is not None:
        await upload_files_task


if __name__ == "__main__":
    asyncio.run(main())
