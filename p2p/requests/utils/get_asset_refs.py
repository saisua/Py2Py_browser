from collections import defaultdict
import asyncio
import logging

from sqlalchemy import select, or_

from config import logger

from db.models.assets import Assets
from db.models.stored_asset_parts import StoredAssetParts
from db.models.asset_hints import AssetHints
from db.models.stored_asset_hashes import StoredAssetHashes
from db.utils.execute import _session_execute


async def get_asset_refs(
    session_maker,
    hashes: dict[str, int | list[int]],
    requested_peer_addrs: list[str],
):
    # TODO: Check for empty dict values
    if not hashes:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"No hashes: {hashes}")
        return None

    full_recv_assets = list()
    recv_assets = defaultdict(list)
    for parts_combination, parts in hashes.items():
        match parts:
            case list():
                recv_assets[parts_combination] = parts
            case -1:
                full_recv_assets.append(parts_combination)
            case int():
                recv_assets[parts_combination].append(parts)
            case _:
                raise ValueError(f"Invalid parts value: {parts}")

    if (
        not full_recv_assets
        and not recv_assets
        and not any(recv_assets)
        and not any(recv_assets.values())
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"No hashes: {full_recv_assets}, {recv_assets}")
        return {
            'status': 0,
            "data": {},
            "hashes": {},
            "hints": {},
            "num_parts": {},
        }

    (
        assets,
        asset_hints,
        stored_asset_hashes,
        stored_asset_parts,
    ) = await asyncio.gather(
        _session_execute(
            session_maker,
            select(Assets).where(
                or_(
                    Assets.hash.in_(full_recv_assets),
                    Assets.hash.in_(recv_assets.keys()),
                )
            ),
            scalar=True,
            many=True,
            expunge=True,
        ),
        _session_execute(
            session_maker,
            select(AssetHints).where(
                AssetHints.address_from.not_in(requested_peer_addrs),
                or_(
                    AssetHints.hash.in_(full_recv_assets),
                    AssetHints.hash.in_(recv_assets.keys()),
                )
            ),
            scalar=True,
            many=True,
            expunge=True,
        ),
        _session_execute(
            session_maker,
            select(StoredAssetHashes).where(
                or_(
                    StoredAssetHashes.hash.in_(full_recv_assets),
                    StoredAssetHashes.hash.in_(recv_assets.keys()),
                )
            ),
            scalar=True,
            many=True,
            expunge=True,
        ),
        _session_execute(
            session_maker,
            select(StoredAssetParts).where(
                or_(
                    StoredAssetParts.hash.in_(full_recv_assets),
                    StoredAssetParts.hash.in_(recv_assets.keys()),
                )
            ),
            scalar=True,
            many=True,
            expunge=True,
        ),
    )

    assets = {asset.hash: asset for asset in assets}

    _stored_asset_parts = dict()
    for part in stored_asset_parts:
        hash_parts = _stored_asset_parts.get(part.hash)
        if hash_parts is None:
            hash_parts = _stored_asset_parts[part.hash] = list()

        hash_parts.append(part.part)
    stored_asset_parts = _stored_asset_parts

    return assets, stored_asset_hashes, asset_hints, stored_asset_parts
