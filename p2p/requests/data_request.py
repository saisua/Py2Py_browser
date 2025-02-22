import os
import asyncio
from datetime import timedelta

from config import data_dir, hashes_dir

from p2p.utils.send_request import send_request

from files.utils.read_bytes import _read_bytes

from p2p.requests.utils.get_asset_refs import get_asset_refs

from p2p.requests.request import Request


class DataRequest(Request):
    CODE = int("1011011", 2)

    def __init__(self, session_maker, *args, **kwargs):
        self.session_maker = session_maker

    async def handle(self, request, *args, **kwargs):
        hashes = request.get('hashes')
        requested_peer_addrs = request.get('requested_peer_addrs')

        asset_refs = await get_asset_refs(
            self.session_maker,
            hashes,
            requested_peer_addrs,
        )

        if asset_refs is None:
            return {
                'status': 0,
                "data": {},
                "hashes": {},
                "hints": {},
                "num_parts": {},
            }

        (
            assets,
            stored_asset_hashes,
            asset_hints,
            stored_asset_parts,
        ) = asset_refs

        load_from_disk_coros = list()

        # Load from disk all asset parts and store them in data
        # TODO: Check for max_timedelta
        added_asset_load = list()
        assets_num_parts = dict()
        missing_parts = dict()
        for asset_hash, asset in assets.items():
            num_parts = asset.num_parts
            parts = stored_asset_parts.get(asset_hash)

            assets_num_parts[asset_hash] = num_parts
            if len(parts) < num_parts:
                missing_parts[asset_hash] = [
                    part
                    for part in range(num_parts)
                    if part not in parts
                ]

            for part in parts:
                part_hash = f"{asset_hash}{part}"
                load_from_disk_coros.append(_read_bytes(
                    os.path.join(data_dir, part_hash),
                    decompress=False,
                ))
                added_asset_load.append(part_hash)

        # Load from disk all stored asset hashes and store them in hashes
        added_stored_asset_hashes = list()
        for stored_asset_hash in stored_asset_hashes:
            for parts_combination in os.listdir(
                os.path.join(hashes_dir, stored_asset_hash.hash)
            ):
                load_from_disk_coros.append(_read_bytes(
                    os.path.join(
                        hashes_dir,
                        stored_asset_hash.hash,
                        parts_combination,
                    ),
                    decompress=False,
                ))
                added_stored_asset_hashes.append(
                    f"{stored_asset_hash.hash}_{parts_combination}"
                )

        loaded_from_disk = await asyncio.gather(*load_from_disk_coros)
        loaded_assets = loaded_from_disk[:len(added_asset_load)]
        loaded_stored_asset_hashes = loaded_from_disk[len(added_asset_load):]

        data = dict()
        for asset_part, loaded_asset_part in zip(
            added_asset_load,
            loaded_assets,
        ):
            data[asset_part] = loaded_asset_part

        hashes = dict()
        for stored_asset_hash, loaded_stored_asset_hash in zip(
            added_stored_asset_hashes,
            loaded_stored_asset_hashes,
        ):
            hashes[stored_asset_hash] = loaded_stored_asset_hash

        # Store all asset hints missing from our asset parts in hints
        # TODO: Filter hints by missing_parts
        hints = dict()
        for hint in asset_hints:
            addr_hint = hints.get(hint.address_from)
            if addr_hint is None:
                addr_hint = hints[hint.address_from] = dict()

            hash_hint = addr_hint.get(hint.hash)
            if hash_hint is None:
                hash_hint = addr_hint[hint.hash] = list()

            hash_hint.append(hint.part)

        return {
            'status': 0,
            "data": data,
            "hashes": hashes,
            "hints": hints,
            "num_parts": assets_num_parts,
        }

    @staticmethod
    async def send(
        addr,
        key,
        hashes: dict[str, int | list[int]],
        requested_peer_addrs: list[str],
        max_timedelta: timedelta | None = None,
    ):
        request = {
            'code': DataRequest.CODE,
            'hashes': hashes,
            'requested_peer_addrs': requested_peer_addrs,
        }
        if max_timedelta is not None:
            request['max_timedelta'] = max_timedelta

        return await send_request(addr, 0, request, large_response=True)
