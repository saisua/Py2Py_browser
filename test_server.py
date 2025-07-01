import asyncio
import os

from config import (
    peer_addr_dir,
    suffix,
)

from p2p.requests.data_request import DataRequest
from p2p.requests.health_check import HealthCheck
from p2p.requests.peer_request import PeerRequest

target_suffix = "_2"
for file in os.listdir(peer_addr_dir):
    if file.endswith(f"-{target_suffix}"):
        target_addr = file.split("-", 1)[0]

send_hc = False
send_peer = True
send_data = False


async def test():
    if send_hc:
        response = await HealthCheck.send(
            target_addr,
            0
        )
        print(response)
    if send_peer:
        response = await PeerRequest.send(
            target_addr,
            0,
            peers=[]
        )
        print(response)
    if send_data:
        response = await DataRequest.send(
            target_addr,
            0,
            {
                "168ce875a2188cce97924a11f6a918df": -1,
                # "d9d604c141a51d24d6d61dafe701e9c9": -1,
                # "a8d95a65de81273e1df5323cdf589879": -1,
                # "75798442c3d3d48b189de5d5f73bbbb9": -1,
                # "32d1337aea77877133ee90d697f718d6": -1
            },
            []
        )
        if response is None:
            print("Response is None")
            return
        status = response["status"]
        if status == 0:
            print({
                "status": status,
                "data": {
                    k: f"<{type(v)} ({len(v)})>"
                    for k, v in response["data"].items()
                },
                "hashes": {
                    k: f"<{type(v)} ({len(v)})>"
                    for k, v in response["hashes"].items()
                },
                "hints": response.get("hints", [])
            })
        else:
            print(response)


if __name__ == "__main__":
    asyncio.run(test())
