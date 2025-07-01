import asyncio
import logging

from sqlalchemy import select

from config import (
    logger,
    DEBUG_DISABLE_DISK_REQUESTS,
    DEBUG_DISABLE_PEER_REQUESTS,
    DEBUG_RESOLVE_REQUESTS_SEQUENTIALLY,
)

from browser.utils.hash_req_res import hash_req_res

from communication.communication import CommunicationUser

from files.browser.load_req_from_disk import load_req_from_disk

from p2p.request_hashes import request_hashes
from p2p.requests.information_request import InformationRequest

from db.peers import Peers, PeerType
from db.utils.execute import _session_execute


_store_response_in_disk_tasks = list()


async def handle_route(
    session_maker,
    comm_user: CommunicationUser,
    route,
    request,
):
    for task_ref in _store_response_in_disk_tasks:
        if task_ref.cancelled() or task_ref.done():
            _store_response_in_disk_tasks.remove(task_ref)

    url = request.url
    domain = request.headers.get("host")
    method = request.method
    headers = request.headers
    url_hash, _ = hash_req_res(url, domain, method, headers)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Request: {request.url}, "
                     f"domain: {domain}, "
                     f"method: {method}, "
                     f"headers: {headers} -> {url_hash}")

    if not DEBUG_DISABLE_PEER_REQUESTS:
        peers = await _session_execute(
            session_maker,
            select(Peers).where(
                Peers.type != PeerType.MYSELF,
            ),
            scalar=True,
            many=True,
            expunge=True,
        )
    else:
        peers = list()

    data_requests = list()

    if not DEBUG_DISABLE_DISK_REQUESTS:
        data_requests.append(load_req_from_disk(url_hash))

    if not DEBUG_DISABLE_PEER_REQUESTS:
        data_requests.extend((
            InformationRequest.send(
                session_maker,
                peer.address,
                peer.sid,
                {url_hash: -1},
                [peer.address for peer in peers],
            )
            for peer in peers
        ))

    # TODO: ask for hints before requesting from peers
    if DEBUG_RESOLVE_REQUESTS_SEQUENTIALLY:
        data_responses = list()
        for i, data_request in enumerate(data_requests, start=1):
            data_response = await data_request
            data_responses.append(data_response)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Data request {i}/{len(data_requests)} done")
    else:
        data_responses = await asyncio.gather(
            *data_requests
        )

    if not DEBUG_DISABLE_DISK_REQUESTS:
        cached_response = data_responses[0]
    else:
        cached_response = None

    if not DEBUG_DISABLE_PEER_REQUESTS:
        peers_info = data_responses[1:]
    else:
        peers_info = list()

    if cached_response:
        if logger.isEnabledFor(logging.INFO):
            logger.info(" (^^)")

        try:
            # print(f"Cached response: {cached_response}")
            await route.fulfill(
                status=200,
                body=cached_response,
            )
            return
        except Exception as e:
            logging.error(e)

    if any((
        peer_info['data_refs']
        for peer_info in peers_info
        if peer_info is not None
    )):
        data = await request_hashes(
            session_maker,
            [url_hash],
            peers,
            peers_info,
        )
        data = data.get(url_hash)
        if data:
            try:
                await route.fulfill(
                    status=200,
                    body=data,
                )
                return
            except Exception as e:
                logging.error(e)

    if logger.isEnabledFor(logging.INFO):
        logger.info(" (>>)")
    await route.continue_()
