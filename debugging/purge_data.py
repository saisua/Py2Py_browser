import shutil
import os
import logging

from config import (
    logger,
    data_dir,
    hashes_dir,
    chat_dir,
    db_dir,
    peer_addr_dir,
)


def purge_data():
    if logger.isEnabledFor(logging.INFO):
        logger.info("Purging data")

    shutil.rmtree(data_dir, ignore_errors=True)
    if logger.isEnabledFor(logging.INFO):
        logger.info("Erased data dir")

    shutil.rmtree(hashes_dir, ignore_errors=True)
    if logger.isEnabledFor(logging.INFO):
        logger.info("Erased hashes dir")

    shutil.rmtree(chat_dir, ignore_errors=True)
    if logger.isEnabledFor(logging.INFO):
        logger.info("Erased chat dir")

    shutil.rmtree(peer_addr_dir, ignore_errors=True)
    if logger.isEnabledFor(logging.INFO):
        logger.info("Erased peer addr dir")

    if os.path.exists(db_dir):
        os.remove(db_dir)
        if logger.isEnabledFor(logging.INFO):
            logger.info("Erased db")
