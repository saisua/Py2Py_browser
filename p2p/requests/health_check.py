from p2p.utils.send_request import send_request

from p2p.requests.request import Request


class HealthCheck(Request):
    CODE = int("0101010", 2)

    def __init__(self, *args, **kwargs):
        pass

    async def handle(self, *args, **kwargs):
        return {'status': 0}

    @staticmethod
    async def send(session_maker, addr, sid):
        print(f"Sending health check request to {addr}", flush=True)

        return await send_request(
            session_maker,
            addr,
            sid,
            {'code': HealthCheck.CODE},
        )
