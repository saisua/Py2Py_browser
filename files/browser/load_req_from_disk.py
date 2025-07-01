import os
import asyncio
import logging

from config import (
    logger,
    data_dir,
)

from files.utils.read_bytes import _read_bytes

from p2p.validate_stored_asset import validate_stored_asset


async def load_req_from_disk(url_hash):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Loading request from disk: {url_hash}")

    url_prefix_len = len(url_hash)

    if not await validate_stored_asset(url_hash):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Request validation failed")
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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Found {len(files)} files")

        data_coros = list()
        for file in files:
            data_coros.append(
                _read_bytes(os.path.join(data_dir, file))
            )
        data = await asyncio.gather(*data_coros)
        return b"".join(data)
    return None
