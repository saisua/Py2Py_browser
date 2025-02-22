import aiofiles

from files.utils.decompress import decompress as decompress_data


async def _read_str(file_path, decompress=True):
    async with aiofiles.open(file_path, "r") as f:
        data = await f.read()

    if decompress:
        data = decompress_data(data)

    return data
