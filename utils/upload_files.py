import os
import asyncio
import logging

from config import files_to_upload_dir

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


def format_file_to_dump(file_to_dump):
    return file_to_dump.replace(" ", "-").lower()


async def upload_files(session_maker):
    files_to_dump_coros = list()
    for file_to_dump in os.listdir(files_to_upload_dir):
        formatted_file_to_dump = format_file_to_dump(file_to_dump)
        url = f"http://{formatted_file_to_dump}.p2p"
        if not os.path.isdir(os.path.join(files_to_upload_dir, file_to_dump)):
            url_hash, domain_hash = hash_req_res(
                f"{url}/",
                "local",
                "GET",
            )
            logging.info("uploading", f"{url}/", url_hash)

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
                            "-",
                            "GET",
                        )

                        logging.info(
                            "uploading",
                            f"{url}/{formatted_folder}/{formatted_file}/",
                            url_hash,
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
