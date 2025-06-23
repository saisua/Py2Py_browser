import asyncio
import bson
import os
import traceback
from datetime import datetime
from functools import partial
from threading import Thread
import logging

from config import (
    num_threads,
    peer_addr_dir,
    DEBUG_ADD_PEERS,
    DEBUG_SHARE_BUNDLE,
    suffix,
)

from communication.communication_user import CommunicationUser

from debugging.add_peers import add_peers_forever

from p2p.requests.data_request import DataRequest
from p2p.requests.health_check import HealthCheck
from p2p.requests.information_request import InformationRequest
from p2p.requests.peer_request import PeerRequest
from p2p.requests.chat_request import ChatRequest
from p2p.utils.addr_to_bytes import addr_to_bytes

from encryption.initialize_encryption import initialize_encryption
from encryption.generate_peer_bundle import _generate_peer_bundle
from encryption.encrypt_message import encrypt_message
from encryption.decrypt_message import decrypt_message

from utils.remove_tasks_forever import remove_tasks_forever


class AsyncBsonServer:
    _REQUEST_HANDLERS_CLASSES = [
        HealthCheck,
        InformationRequest,
        PeerRequest,
        DataRequest,
        ChatRequest,
    ]
    REQUEST_HANDLERS: dict = dict()

    stopped = asyncio.Event()
    _main_thread = None
    _instance_sizes: dict
    _instance_ports: list
    _instance_lock: asyncio.Lock

    _ref_tasks: list
    _ref_task_del: asyncio.Task

    comm_user: CommunicationUser

    def __init__(
        self,
        session_maker,
        comm_user: CommunicationUser,
        host='::1',
        port=None,
        *,
        num_threads=num_threads,
    ):
        self.session_maker = session_maker
        self._instance_sizes = dict()
        self._instance_ports = list()
        self._instance_lock = asyncio.Lock()

        self._ref_tasks = list()
        self._ref_task_del = None

        self.comm_user = comm_user

        self.host = host
        self.port = port
        self.num_threads = num_threads
        self.REQUEST_HANDLERS = {
            handler.CODE: handler(session_maker)
            for handler in self._REQUEST_HANDLERS_CLASSES
        }

    async def initialize_encryption(self, address):
        await initialize_encryption(self.session_maker, address)

    async def write_error(self, writer):
        response = {"status": -1}
        writer.write(bson.dumps(response))
        await writer.drain()

    async def handle_client(self, reader, writer, own_port_i):
        # Possible DOS when attacking all ports before
        # correct initialization
        port = self._instance_ports[own_port_i]
        (_, sid, data_len) = self._instance_sizes[port]
        try:
            ip, port = writer.get_extra_info('peername')[:2]
            addr_str = f"{ip}:{port}"

            logging.debug(f"Received {data_len}B request from {addr_str}")

            data = b""
            while len(data) < data_len:
                data += await reader.read(data_len - len(data))

            logging.debug(f"Received {len(data)}B from {addr_str}")

            if not data:
                logging.warning(f"no data / {data_len}")
                return

            decrypted_data = await decrypt_message(
                self.session_maker,
                data,
                sid
            )
            request = bson.loads(decrypted_data)

            if not request.get('code'):
                logging.warning("no code")
                await self.write_error(writer)
                return

            request_code = request.get('code')

            handler = self.REQUEST_HANDLERS.get(request_code)
            if not handler:
                logging.warning(f"invalid code {request_code}")
                await self.write_error(writer)
                return

            response = await handler.handle(request)
            bin_response = bson.dumps(response)
            encrypted_response = await encrypt_message(
                self.session_maker,
                bin_response,
                sid
            )

            logging.debug(f"Responding {len(bin_response)} bytes")

            writer.write(len(encrypted_response).to_bytes(4, 'big'))
            await writer.drain()
            writer.write(encrypted_response)
            await writer.drain()
        except Exception:
            logging.error(traceback.format_exc())
            await self.write_error(writer)
        finally:
            writer.close()
            _, resetted_port = await asyncio.gather(
                writer.wait_closed(),
                self._set_data_size(port, 0, check_unoccupied=False),
            )

            # logging.debug(f"[{port}] closed")
            logging.debug(f"[{port}] request closed")

    async def _set_data_size(
        self,
        port,
        size,
        *,
        check_unoccupied=True,
    ) -> bool:
        async with self._instance_lock:
            if check_unoccupied and self._instance_sizes.get(port) != 0:
                return False

            self._instance_sizes[port] = size
            return True

    async def redirect_request(self, reader, writer):
        try:
            first_payload: bytes = await reader.read(8)
            if not first_payload:
                logging.warning("No payload received")
                return

            if first_payload == b'\x00' * 8:
                logging.warning("Empty payload received")
                return

            data_len = int.from_bytes(first_payload[4:], 'big')
            if data_len > 2**31:
                logging.warning(f"data_len is too large {data_len}")
                writer.write(b'\x00' * 4)
                await writer.drain()
                return

            sid = int.from_bytes(first_payload[:4], 'big')

            for _ in range(100):
                for port, size in self._instance_sizes.items():
                    if (
                        size == 0
                        and  # noqa: W503 W504
                        await self._set_data_size(
                            port,
                            (datetime.now(), sid, data_len),
                        )
                    ):
                        writer.write(port.to_bytes(4, 'big'))
                        await writer.drain()
                        return
                    logging.debug(f"port {port} is handling {size}")
                await asyncio.sleep(0.15)
                logging.debug("waiting for data size")
            else:
                logging.critical("No port found")
        except Exception as e:
            logging.error(e)
            return None

    async def start_server(self):
        server = await asyncio.start_server(
            self.redirect_request, self.host, self.port
        )
        addr = server.sockets[0].getsockname()
        logging.info(f'Serving on {addr}')

        servers = [server]
        for i in range(self.num_threads):
            servers.append(
                await asyncio.start_server(
                    partial(self.handle_client, own_port_i=i), self.host
                )
            )

            port = servers[-1].sockets[0].getsockname()[1]
            self._instance_sizes[port] = 0
            self._instance_ports.append(port)

            logging.info(f" instance {i} started on port {port}")

        addr_str = ':'.join(map(str, addr[:2]))
        addr = addr_to_bytes(*addr[:2])
        await initialize_encryption(self.session_maker, addr)

        if DEBUG_SHARE_BUNDLE:
            # It should be encrypted but its for debugging
            encryption_data = await _generate_peer_bundle(
                self.session_maker,
                addr,
            )

            os.makedirs(peer_addr_dir, exist_ok=True)

            for file in os.listdir(peer_addr_dir):
                if file.endswith(f"-{suffix}"):
                    os.remove(os.path.join(peer_addr_dir, file))

            with open(
                os.path.join(peer_addr_dir, f"{addr_str}-{suffix}"),
                "wb+",
            ) as f:
                f.write(encryption_data)

        if DEBUG_ADD_PEERS:
            self._ref_tasks.append(
                asyncio.create_task(
                    add_peers_forever(self.session_maker)
                )
            )

        self._ref_task_del = asyncio.create_task(
            remove_tasks_forever(self._ref_tasks)
        )

        server_tasks = []
        try:
            for server in servers:
                await server.__aenter__()

                server_task = asyncio.create_task(server.serve_forever())
                server_tasks.append(server_task)

            while not self.stopped.is_set():
                await asyncio.sleep(1)

        except Exception:
            logging.error(traceback.format_exc())
        finally:
            exit_coros = list()
            for server, server_task in zip(servers, server_tasks):
                server_task.cancel()
                exit_coros.append(server.__aexit__())
            await asyncio.gather(*exit_coros)

    def start_server_sync(self):
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            pass

    def start(self):
        self._main_thread = Thread(
            target=self.start_server_sync,
            daemon=True,
        )
        self._main_thread.start()

    def stop(self):
        self.stopped.set()
        self._main_thread.join()
