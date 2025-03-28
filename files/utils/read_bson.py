import aiofiles

import bson

from files.utils.decompress import decompress as decompress_data


async def _read_bson(file_path, decompress=True):
    async with aiofiles.open(file_path, "rb") as f:
        data = await f.read()

    if decompress:
        data = decompress_data(data)

    return bson.loads(data)
