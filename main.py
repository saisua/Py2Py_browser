import asyncio
import os
import shutil

from config import (
    data_path,
    data_dir,
    hashes_dir,
    db_dir,
    DEBUG_PURGE_DATA,
    UPLOAD_FILES,
    DEBUG_ADD_PEER,
)

if DEBUG_PURGE_DATA:
    shutil.rmtree(data_dir, ignore_errors=True)
    print("Erased data dir", flush=False)
    shutil.rmtree(hashes_dir, ignore_errors=True)
    print("Erased hashes dir", flush=False)
    if os.path.exists(db_dir):
        os.remove(db_dir)
    print("Erased db", flush=False)

from db import session_maker, engine

from p2p.server import AsyncBsonServer

from browser.run_browser import run_browser

from utils.upload_files import upload_files

if DEBUG_ADD_PEER:
    from datetime import datetime

    from db.peers import Peers
    from db.utils.add import _session_add

    if os.path.exists(f"{data_path}/address_2.txt"):
        with open(f"{data_path}/address_2.txt", "r") as f:
            addr = f.read()

        try:
            asyncio.run(
                _session_add(
                    session_maker,
                    Peers(
                        address=addr,
                        type=0,
                        checked_time=datetime.now(),
                    ),
                )
            )
            print(f"Added peer {addr}", flush=False)
        except Exception as e:
            print(e)


async def main():
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(hashes_dir, exist_ok=True)

    server = AsyncBsonServer(session_maker)
    server.start()

    if UPLOAD_FILES:
        print("Uploading files", flush=False)
        upload_files_task = asyncio.create_task(
            upload_files(session_maker)
        )
    else:
        upload_files_task = None

    try:
        await run_browser(session_maker)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        await engine.dispose()
        server.stop()

    if upload_files_task is not None:
        await upload_files_task


if __name__ == "__main__":
    asyncio.run(main())
