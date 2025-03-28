import aiofiles

from files.utils.read_bytes import _read_bytes


async def _read_str(file_path, decompress=True):
    if decompress:
        data = (await _read_bytes(file_path, decompress=True)).decode()
    else:
        async with aiofiles.open(file_path, "r") as f:
            data = await f.read()

    return data
