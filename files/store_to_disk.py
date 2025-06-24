import os
import random
from datetime import datetime
import asyncio
import hashlib
import logging

from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError

from config import data_dir, hashes_dir, n_hashes, split_size

from db import Assets, StoredAssetParts, StoredAssetHashes
from db.utils.add_all import _session_add_all
from db.utils.execute import _session_execute

from files.utils.store_bytes import _store_bytes
from files.utils.store_str import _store_str


async def store_to_disk(session_maker, url_hash, domain_hash, data):
    logging.debug(f"Storing to disk: {url_hash} {domain_hash}")

    data_splits = []
    for i in range(0, len(data), split_size):
        data_splits.append(data[i:i + split_size])

    new_asset_parts = []
    # Store or update asset and asset parts
    asset = await _session_execute(
        session_maker,
        select(Assets.hash)
        .where(Assets.hash == url_hash)
    )
    asset = asset.scalar()

    store_coros = []
    if asset is not None:
        logging.debug(f"Updating asset: {url_hash}")

        store_coros.append(
            _session_execute(
                session_maker,
                update(Assets)
                .where(Assets.hash == url_hash)
                .values(
                    num_parts=len(data_splits),
                    created_time=datetime.now(),
                ), commit=True
            )
        )
    else:
        logging.debug(f"Adding asset: {url_hash}")

        try:
            await _session_add_all(
                session_maker,
                (Assets(
                    hash=url_hash,
                    domain_hash=domain_hash,
                    num_parts=len(data_splits),
                    created_time=datetime.now(),
                ),)
            )
        except IntegrityError as e:
            logging.error(e)
            return

    logging.debug(f"Storing {len(data_splits)} data splits to disk")
    for i, data_split in enumerate(data_splits):
        file_path = os.path.join(data_dir, f"{url_hash}{i}")

        store_coros.append(_store_bytes(file_path, data_split))

        new_asset_parts.append(StoredAssetParts(
            hash=url_hash,
            part=i,
            stored_dt=datetime.now(),
        ))

    if len(data_splits) != 1:
        logging.debug(f"Getting max hash num for {url_hash}")
        store_coros.append(_session_execute(
            session_maker,
            select(
                func.max(StoredAssetHashes.id)
            ).where(StoredAssetHashes.hash == url_hash)
        ))

    hashes_folder = os.path.join(hashes_dir, url_hash)
    if not os.path.exists(hashes_folder):
        logging.debug(f"Creating hashes folder: {hashes_folder}")
        os.makedirs(hashes_folder, exist_ok=True)

    # Get max id of stored_asset_hashes
    store_results = await asyncio.gather(
        *store_coros,
        _session_add_all(session_maker, new_asset_parts),
        return_exceptions=True,
    )
    store_coros.clear()
    new_asset_parts.clear()

    if len(data_splits) != 1:
        max_hash_num = store_results[-1]

        if max_hash_num is None:
            max_hash_num = 0
        elif isinstance(max_hash_num, IntegrityError):
            logging.error(max_hash_num)
            max_hash_num = 0
        else:
            max_hash_num = max_hash_num.scalar() + 1
    else:
        max_hash_num = 0

    logging.debug(f"Generating {n_hashes} hashes for {url_hash}")

    new_hashes = []
    hashed = set()
    for new_hash_num in range(min(n_hashes, len(data_splits) ** 2)):
        if len(data_splits) == 1:
            combination_indices = (0,)
        else:
            combination_indices = tuple(
                random.sample(
                    list(range(len(data_splits))),
                    random.randint(1, min(len(data_splits), 16))
                )
            )

        if combination_indices in hashed:
            continue

        hashed.add(combination_indices)

        hash_file = os.path.join(
            hashes_folder,
            f"{'_'.join(map(str, combination_indices))}"
        )
        if os.path.exists(hash_file):
            continue

        hashed_data = []
        for ind in combination_indices:
            hashed_data.append(data_splits[ind])

        hash = hashlib.sha256(b"".join(hashed_data)).hexdigest()
        store_coros.append(_store_str(hash_file, hash))
        new_hashes.extend((
            StoredAssetHashes(
                hash=url_hash,
                id=max_hash_num + new_hash_num,
                part=ind,
                stored_dt=datetime.now(),
            )
            for ind in combination_indices
        ))

    logging.debug(f"Storing {len(new_hashes)} hashes to disk")

    await asyncio.gather(
        *store_coros,
        _session_add_all(session_maker, new_hashes),
        return_exceptions=True,
    )
