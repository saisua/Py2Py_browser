import aiofiles

from files.utils.store_bytes import _store_bytes


async def _store_str(path, data, compress=True):
    if compress:
        await _store_bytes(path, data.encode(), compress=True)
    else:
        async with aiofiles.open(path, "w+") as f:
            await f.write(data)

