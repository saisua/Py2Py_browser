import asyncio
import bson
import os
import traceback
from functools import partial
from threading import Thread

from config import suffix, data_path, num_threads

from p2p.requests.data_request import DataRequest
from p2p.requests.health_check import HealthCheck
from p2p.requests.information_request import InformationRequest
from p2p.requests.peer_request import PeerRequest


class AsyncBsonServer:
    _REQUEST_HANDLERS_CLASSES = [
        HealthCheck,
        InformationRequest,
        PeerRequest,
        DataRequest,
    ]
    REQUEST_HANDLERS: dict = dict()

    stopped = asyncio.Event()
    _main_thread = None
    _instance_sizes: dict
    _instance_ports: list
    _instance_lock: asyncio.Lock

    def __init__(
        self,
        session_maker,
        host='127.0.0.1',
        port=None,
        *,
        num_threads=num_threads,
    ):
        self.session_maker = session_maker
        self._instance_sizes = dict()
        self._instance_ports = list()
        self._instance_lock = asyncio.Lock()

        self.host = host
        self.port = port
        self.num_threads = num_threads
        self.REQUEST_HANDLERS = {
            handler.CODE: handler(session_maker)
            for handler in self._REQUEST_HANDLERS_CLASSES
        }

    async def write_error(self, writer):
        response = {"status": -1}
        writer.write(bson.dumps(response))
        await writer.drain()

    async def handle_client(self, reader, writer, own_port_i):
        port = self._instance_ports[own_port_i]
        data_len = self._instance_sizes[port]
        try:
            # print(f"data_len: {data_len}", flush=False)

            data = b""
            while len(data) < data_len:
                data += await reader.read(data_len - len(data))

            if not data:
                print(f"no data / {data_len}")
                return

            request = bson.loads(data)

            if not request.get('code'):
                print("no code")
                await self.write_error(writer)
                return

            request_code = request.get('code')

            handler = self.REQUEST_HANDLERS.get(request_code)
            if not handler:
                print(f"invalid code {request_code}")
                await self.write_error(writer)
                return

            response = await handler.handle(request)
            bin_response = bson.dumps(response)
            # print(f"Responding {len(bin_response)} bytes")
            writer.write(len(bin_response).to_bytes(4, 'big'))
            await writer.drain()
            writer.write(bin_response)
            await writer.drain()
        except Exception:
            print(traceback.format_exc())
            await self.write_error(writer)
        finally:
            writer.close()
            _, resetted_port = await asyncio.gather(
                writer.wait_closed(),
                self._set_data_size(port, 0, check_unoccupied=False),
            )

            # print(f"[{port}] closed", flush=False)
            print(f"[{port}] request closed", flush=False)

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
            data_len = await reader.read(1024)
            if not data_len:
                return

            data_len = int.from_bytes(data_len, 'big')
            if data_len == 0:
                return
            if data_len > 2**31:
                print("data_len is too large")
                return

            for _ in range(100):
                for port, size in self._instance_sizes.items():
                    if size == 0:
                        if await self._set_data_size(port, data_len):
                            writer.write(port.to_bytes(4, 'big'))
                            await writer.drain()
                            return
                    # print(f"port {port} is handling {size}", flush=False)
                await asyncio.sleep(0.15)
                # print("waiting for data size", flush=False)
        except Exception:
            return None

    async def start_server(self):
        server = await asyncio.start_server(
            self.redirect_request, self.host, self.port
        )
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

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

            print(f" instance {i} started on port {port}")

        with open(os.path.join(data_path, f"address{suffix}.txt"), "w") as f:
            f.write(':'.join(map(str, addr)))

        server_tasks = []
        try:
            for server in servers:
                await server.__aenter__()

                server_task = asyncio.create_task(server.serve_forever())
                server_tasks.append(server_task)

            while not self.stopped.is_set():
                await asyncio.sleep(1)

        except Exception:
            print(traceback.format_exc())
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
