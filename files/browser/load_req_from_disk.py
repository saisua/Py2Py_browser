import os
import asyncio
import logging

from config import data_dir

from files.utils.read_bytes import _read_bytes

from p2p.validate_stored_asset import validate_stored_asset


async def load_req_from_disk(url_hash):
    logging.debug(f"Loading request from disk: {url_hash}")

    url_prefix_len = len(url_hash)

    if not await validate_stored_asset(url_hash):
        logging.debug("Request validation failed")
        return None

    files = sorted(
        (
            file
            for file in os.listdir(data_dir)
            if file.startswith(url_hash)
        ),
        key=lambda file: int(file[url_prefix_len:], 16)
    )
    if files:
        logging.debug(f"Found {len(files)} files")

        data_coros = list()
        for file in files:
            data_coros.append(
                _read_bytes(os.path.join(data_dir, file))
            )
        data = await asyncio.gather(*data_coros)
        return b"".join(data)
    return None
