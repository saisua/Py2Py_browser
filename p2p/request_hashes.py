import random
import asyncio
import os

import numpy as np

from config import data_dir

from p2p.requests.data_request import DataRequest

from db.peers import Peers

from files.utils.store_bytes import _store_bytes
from files.utils.decompress import decompress as decompress_data


def choose_peer_requests(
    peers: list["Peers"],
    peers_info: list[dict],
):
    # Decide each url_hash how many parts has based on peers_info
    # Then split the parts from the url_hashes to be requested from peers
    # Return each peer what parts from what url_hash to request
    url_hashes_num_parts = {}
    for peer_info in peers_info:
        for url_hash, num_parts in peer_info['num_parts'].items():
            num_parts_list = url_hashes_num_parts.get(url_hash)
            if num_parts_list is None:
                url_hashes_num_parts[url_hash] = [num_parts]
            else:
                num_parts_list.append(num_parts)

    for url_hash, num_parts_list in url_hashes_num_parts.items():
        # TODO: Do not request from one peer if it has all parts
        num_parts = num_parts_list[0]
        if any((num_parts != num_parts_ for num_parts_ in num_parts_list[1:])):
            url_hashes_num_parts.pop(url_hash)
        else:
            url_hashes_num_parts[url_hash] = num_parts

    peer_parts = dict()
    for url_hash, num_parts in peer_info['num_parts'].items():
        hash_parts = peer_parts.get(url_hash)
        if hash_parts is None:
            hash_parts = peer_parts[url_hash] = dict()

        for peer_num, (peer, peer_info) in enumerate(zip(peers, peers_info)):
            parts = peer_info["data_refs"].get(url_hash)
            if parts is None:
                continue

            for part in parts:
                part_peers = hash_parts.get(part)
                if part_peers is None:
                    part_peers = hash_parts[part] = list()

                part_peers.append((peer.address, peer_num))

    peer_weights = np.array([
        1.0
        for _ in range(len(peers))
    ])
    peer_reqs = {
        peer.address: dict()
        for peer in peers
    }
    for hash, parts in peer_parts.items():
        for part, peer_addrs in parts.items():
            chosen_peer_addr, chosen_peer_num = random.choices(
                peer_addrs,
                weights=peer_weights,
                k=1,
            )[0]
            peer_weights[chosen_peer_num] /= 2

            peer_hash_parts = peer_reqs[chosen_peer_addr].get(hash)
            if peer_hash_parts is None:
                peer_hash_parts = peer_reqs[chosen_peer_addr][hash] = list()

            peer_hash_parts.append(part)

            if peer_weights.min() < 1e-3:
                peer_weights = np.exp(peer_weights - peer_weights.max())
                peer_weights /= peer_weights.sum()

    return peer_reqs, url_hashes_num_parts


_store_response_in_disk_tasks = []


async def request_hashes(
    session_maker,
    url_hashes: list[str],
    peers: list[str],
    peers_info: list[dict],
):
    for task in _store_response_in_disk_tasks:
        if task.done() or task.cancelled():
            _store_response_in_disk_tasks.remove(task)

    peer_reqs, url_hashes_num_parts = choose_peer_requests(peers, peers_info)

    all_peer_addrs = [peer.address for peer in peers]

    recv_responses = await asyncio.gather(*(
        DataRequest.send(peer_addr, 0, request_hashes, all_peer_addrs)
        for peer_addr, request_hashes in peer_reqs.items()
    ))
    url_data = dict()
    for url_hash in url_hashes:
        url_data_parts = dict()
        for recv_response in recv_responses:
            if (
                recv_response is None
                or not any((
                    key.startswith(url_hash)
                    for key in recv_response['data']
                ))
                or recv_response['num_parts'].get(url_hash, 0) == 0
            ):
                continue

            print(" (~~)", flush=False)

            for part_hash, part_data in recv_response['data'].items():
                _store_response_in_disk_tasks.append(
                    asyncio.create_task(
                        _store_bytes(
                            os.path.join(data_dir, part_hash),
                            part_data,
                            compress=False,
                        )
                    )
                )

            for key, part_data in (
                (k, v) for k, v in recv_response['data'].items()
                if k.startswith(url_hash)
            ):
                url_data_parts[key] = part_data

        num_parts = url_hashes_num_parts.get(url_hash)
        if num_parts is None or len(url_data_parts) != num_parts:
            continue

        len_url_hash = len(url_hash)
        url_data[url_hash] = b"".join((
            decompress_data(v)
            for k, v in sorted(
                url_data_parts.items(),
                key=lambda item: int(item[0][len_url_hash:]),
            )
        ))

    return url_data
