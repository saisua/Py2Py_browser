import asyncio
import os
import logging

from config import (
    logger,
    data_dir,
)

from browser.utils.hash_req_res import hash_req_res

from files.store_to_disk import store_to_disk

store_data_tasks = list()


async def store_res_to_disk(session_maker, response):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Storing response to disk")

    for task in store_data_tasks:
        if task.done() or task.cancelled():
            store_data_tasks.remove(task)

    url = response.url
    domain = response.request.headers.get("host")
    method = response.request.method
    headers = response.request.headers
    url_hash, domain_hash = hash_req_res(url, domain, method, headers)

    if any((
        True
        for file in os.listdir(data_dir)
        if file.startswith(url_hash)
    )):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Response already stored")
        return

    try:
        body = await response.body()
    except Exception as e:
        logging.error(e)
        return

    store_data_tasks.append(
        asyncio.create_task(
            store_to_disk(session_maker, url_hash, domain_hash, body)
        )
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"<< {url}")
