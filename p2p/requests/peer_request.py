from datetime import datetime
import asyncio
import logging

from sqlalchemy import select

from config import (
    logger,
    PEERTYPE_CLIENT,
)
from db.peers import Peers

from db.utils.add_all import _session_add_all

from encryption.decrypt_message import decrypt_message

from p2p.requests.health_check import HealthCheck

from p2p.utils.send_request import send_request

from p2p.requests.request import Request


async def store_online_peers(session_maker, peer_addrs, sids):
    health_check_coros = []
    for address, sid in zip(peer_addrs, sids):
        # TODO: Use key
        health_check_coros.append(
            HealthCheck.send(session_maker, address, sid)
        )

    responses = await asyncio.gather(*health_check_coros)

    # print(responses)

    now = datetime.now()
    # TODO: Use key
    new_peers = [
        Peers(
            address=address,
            checked_time=now,
            type=PEERTYPE_CLIENT,
        )
        for address, response in zip(peer_addrs, responses)
        if "status" in response and response['status'] == 0
    ]

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"New peers: {new_peers}")

    await _session_add_all(session_maker, new_peers)


class PeerRequest(Request):
    _peer_verification_task_refs: list[asyncio.Task] = list()
    CODE = int("1010101", 2)

    def __init__(self, session_maker, *args, **kwargs):
        self.session_maker = session_maker

    async def handle(self, request, *args, **kwargs):
        for task in self._peer_verification_task_refs:
            if task.done() or task.cancelled():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Task done")
                self._peer_verification_task_refs.remove(task)

        async with self.session_maker() as session:
            async with session.begin():
                peers = await session.execute(select(Peers))

        recv_peer_addrs = request.get('peers')
        if recv_peer_addrs:
            # TODO: Fix encryption
            peer_addrs = [
                peer.address for peer in peers
            ]
            decrypted_recv_peer_addrs = set(filter(
                None,
                (
                    decrypt_message(peer) for peer in recv_peer_addrs
                )
            ))

            # new_peer_addrs = (
            #     decrypted_recv_peer_addrs - set(decrypted_peer_addrs)
            # )
            # TODO: When peer connection is enabled
            # self._peer_verification_task_refs.append(
            #     asyncio.create_task(
            #         store_online_peers(self.session_maker, new_peer_addrs)
            #     )
            # )

            # Send the encrypted peer addresses to the sender
            peer_addrs = [
                peer.address
                for peer_num, peer in enumerate(peers)
                if peer_addrs[peer_num]
                not in decrypted_recv_peer_addrs
            ]
        else:
            peer_addrs = [
                peer.address
                for peer in peers
            ]

        return {'status': 0, 'peers': peer_addrs}

    @staticmethod
    async def send(session_maker, addr, sid, peers=None):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Sending peer request to {addr}")

        request = {
            'code': PeerRequest.CODE,
        }
        if peers:
            request['peers'] = peers
        return await send_request(session_maker, addr, sid, request)
