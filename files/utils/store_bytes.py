import aiofiles

from files.utils.compress import compress as compress_data


async def _store_bytes(path, data, compress=True):
    if compress:
        data = compress_data(data)

    async with aiofiles.open(path, "wb+") as f:
        await f.write(data)
