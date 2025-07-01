from itertools import chain
import os
import asyncio
import logging

from config import (
	logger,
	files_to_upload_dir,
	supported_video_extensions,
	supported_audio_extensions,
)

from file_upload.upload_media import upload_media
from file_upload.utils.format_file import format_file_to_dump

from browser.utils.hash_req_res import hash_req_res

from files.store_to_disk import store_to_disk
from files.utils.read_bytes import _read_bytes


async def read_file_store_to_disk(
    session_maker,
    file_path,
    url_hash,
    domain_hash,
):
    await store_to_disk(
        session_maker,
        url_hash,
        domain_hash,
        await _read_bytes(file_path, decompress=False),
    )


async def upload_files(session_maker, files=None):
    if files is None:
        files = os.listdir(files_to_upload_dir)
        if logger.isEnabledFor(logging.INFO):
            logger.info(
                f"uploading {len(files)} files from {files_to_upload_dir}"
            )
    else:
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"uploading {len(files)} files")

    files_to_dump_coros = list()
    for file_to_dump in files:
        if file_to_dump.startswith("."):
            continue

        formatted_file_to_dump = format_file_to_dump(file_to_dump)
        domain = f"{formatted_file_to_dump}.p2p"
        url = f"http://{domain}"

        if not os.path.isdir(os.path.join(files_to_upload_dir, file_to_dump)):
            if any(
                True
                for ext in chain(
                    supported_video_extensions,
                    supported_audio_extensions,
                )
                if file_to_dump.endswith(ext)
            ):
                await upload_media(
                    session_maker,
                    os.path.join(files_to_upload_dir, file_to_dump),
                )
            else:
                url_hash, domain_hash = hash_req_res(
                    f"{url}/",
                    domain,
                    "GET",
                )
                if logger.isEnabledFor(logging.INFO):
                    logger.info(f"uploading {url}/ {url_hash}")

                files_to_dump_coros.append(
                    read_file_store_to_disk(
                        session_maker,
                        os.path.join(files_to_upload_dir, file_to_dump),
                        url_hash,
                        domain_hash,
                    )
                )
        else:
            for folder, _, files in os.walk(
                os.path.join(files_to_upload_dir, file_to_dump)
            ):
                formatted_folder = format_file_to_dump(folder)
                for file in files:
                    if not os.path.isdir(os.path.join(folder, file)):
                        formatted_file = format_file_to_dump(file)

                        url_hash, domain_hash = hash_req_res(
                            f"{url}/{formatted_folder}/{formatted_file}/",
                            domain,
                            "GET",
                        )

                        if logger.isEnabledFor(logging.INFO):
                            logger.info(
                                "uploading folder "
                                f"{url}/{formatted_folder}/{formatted_file}/"
                                f" {url_hash}"
                            )

                        files_to_dump_coros.append(
                            read_file_store_to_disk(
                                session_maker,
                                os.path.join(folder, file),
                                url_hash,
                                domain_hash,
                            )
                        )

    await asyncio.gather(*files_to_dump_coros)
