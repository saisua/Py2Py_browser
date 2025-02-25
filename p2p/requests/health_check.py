from p2p.utils.send_request import send_request

from p2p.requests.request import Request


class HealthCheck(Request):
    CODE = int("0101010", 2)

    def __init__(self, *args, **kwargs):
        pass

    async def handle(self, *args, **kwargs):
        return {'status': 0}

    @staticmethod
    async def send(addr, key):
        return await send_request(
            addr,
            key,
            {'code': HealthCheck.CODE},
        )
