import asyncio

from sqlalchemy import select

from browser.utils.hash_req_res import hash_req_res

from files.load_req_from_disk import load_req_from_disk

from p2p.request_hashes import request_hashes
from p2p.requests.information_request import InformationRequest

from db.peers import Peers
from db.utils.execute import _session_execute

_store_response_in_disk_tasks = list()


async def handle_route(session_maker, route, request):
    for task_ref in _store_response_in_disk_tasks:
        if task_ref.cancelled() or task_ref.done():
            _store_response_in_disk_tasks.remove(task_ref)

    url = request.url
    domain = request.headers.get("host")
    method = request.method
    headers = request.headers
    url_hash, _ = hash_req_res(url, domain, method, headers)

    print(">>", request.url, url_hash, flush=False)

    peers = await _session_execute(
        session_maker,
        select(Peers),
        scalar=True,
        many=True,
        expunge=True,
    )

    # TODO: ask for hints before requesting from peers
    cached_response, *peers_info = await asyncio.gather(
        load_req_from_disk(url_hash),
        *(
            InformationRequest.send(
                peer.address,
                0,
                {url_hash: -1},
                [peer.address for peer in peers],
            )
            for peer in peers
        )
    )
    if cached_response:
        print(" (^^)", flush=False)
        await route.fulfill(
            status=200,
            body=cached_response,
        )
        return

    if any((
        pi['data_refs']
        for pi in peers_info
        if pi is not None
    )):
        data = await request_hashes(
            session_maker,
            [url_hash],
            peers,
            peers_info,
        )
        data = data.get(url_hash)
        if data:
            await route.fulfill(
                status=200,
                body=data,
            )
            return

    print(" (>>)", flush=False)
    await route.continue_()
