import os
import logging

from config import hashes_dir

from p2p.utils.send_request import send_request

from p2p.requests.utils.get_asset_refs import get_asset_refs

from p2p.requests.request import Request


class InformationRequest(Request):
    CODE = int("1001001", 2)

    def __init__(self, session_maker, *args, **kwargs):
        self.session_maker = session_maker

    async def handle(self, request, *args, **kwargs):
        hashes = request.get('hashes')
        # requested_peer_addrs = request.get('requested_peer_addrs')

        asset_refs = await get_asset_refs(
            self.session_maker,
            hashes,
            [],
            # requested_peer_addrs,
        )

        if asset_refs is None:
            logging.debug("No asset refs found")
            return {
                'status': 0,
                "data_refs": {},
                "hashes_refs": {},
                "hints": {},
                "num_parts": {},
            }

        (
            assets,
            stored_asset_hashes,
            asset_hints,
            stored_asset_parts,
        ) = asset_refs

        data_refs = dict()
        assets_num_parts = dict()
        for asset_hash, asset in assets.items():
            num_parts = asset.num_parts
            parts = stored_asset_parts.get(asset_hash)

            assets_num_parts[asset_hash] = num_parts
            data_refs[asset_hash] = [
                f"{asset_hash}{part}"
                for part in parts
            ]

        # Load from disk all stored asset hashes and store them in hashes
        hashes_refs = dict()
        for stored_asset_hash in stored_asset_hashes:
            hash_hashes = hashes_refs.get(stored_asset_hash.hash)
            if hash_hashes is None:
                hash_hashes = hashes_refs[stored_asset_hash.hash] = list()

            for parts_combination in os.listdir(
                os.path.join(hashes_dir, stored_asset_hash.hash)
            ):
                hash_hashes.append(parts_combination)

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
            "data_refs": data_refs,
            "hashes_refs": hashes_refs,
            "hints": hints,
            "num_parts": assets_num_parts,
        }

    @staticmethod
    async def send(
        session_maker,
        addr,
        sid,
        hashes: dict[str, int | list[int]],
        requested_peer_addrs: list[str],
    ):
        print(f"Sending information request to {addr}", flush=True)

        request = {
            'code': InformationRequest.CODE,
            'hashes': hashes,
            'requested_peer_addrs': requested_peer_addrs,
        }

        return await send_request(
            session_maker,
            addr,
            sid,
            request,
            large_response=False,
        )
