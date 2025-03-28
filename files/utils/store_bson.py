import aiofiles

import bson

from files.utils.compress import compress as compress_data


async def _store_bson(path, data, compress=True):
    data = bson.dumps(data)

    if compress:
        data = compress_data(data)

    async with aiofiles.open(path, "wb+") as f:
        await f.write(data)
