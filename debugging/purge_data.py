import shutil
import os
import logging

from config import (
    data_dir,
    hashes_dir,
    chat_dir,
    db_dir,
    peer_addr_dir,
)


def purge_data():
    logging.info("Purging data")
    shutil.rmtree(data_dir, ignore_errors=True)
    logging.info("Erased data dir")
    shutil.rmtree(hashes_dir, ignore_errors=True)
    logging.info("Erased hashes dir")
    shutil.rmtree(chat_dir, ignore_errors=True)
    logging.info("Erased chat dir")
    shutil.rmtree(peer_addr_dir, ignore_errors=True)
    logging.info("Erased peer addr dir")
    if os.path.exists(db_dir):
        os.remove(db_dir)
    logging.info("Erased db")
