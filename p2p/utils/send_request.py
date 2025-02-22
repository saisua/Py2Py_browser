import asyncio
import bson
import traceback

from encryption.encrypt_message import encrypt_message
from encryption.decrypt_message import decrypt_message


async def send_request(addr, key, request, *, large_response=False):
    ip, port = addr.split(":")
    try:
        reader, writer = await asyncio.open_connection(
            ip,
            port,
        )
    except Exception:
        print(f"address {addr} is not available")
        return None

    bson_req = bson.dumps(request)
    encrypted_req = encrypt_message(bson_req, key)

    # print(f"Sending {len(encrypted_req)} bytes")

    writer.write(len(encrypted_req).to_bytes(4, 'big'))
    await writer.drain()

    new_port = await reader.read(4)
    if not new_port:
        return None

    new_port = int.from_bytes(new_port, 'big')
    # print(f"Redirected to {new_port}")

    limit = 2**32 if large_response else 2**16
    try:
        reader, writer = await asyncio.open_connection(
            ip,
            new_port,
            limit=limit,
        )
    except Exception:
        print(f"address {addr} is not available")
        return None

    writer.write(encrypted_req)
    await writer.drain()

    res_len = int.from_bytes(await reader.read(4), 'big')

    # if res_len > limit:
    #     print("Response is too large")
    #     return None

    # print(f"Receiving {res_len} bytes")

    encrypted_res = b""
    while len(encrypted_res) < res_len:
        encrypted_res += await reader.read(res_len - len(encrypted_res))

    res = decrypt_message(encrypted_res, addr=addr)

    try:
        return bson.loads(res)
    except Exception:
        print(traceback.format_exc())
        return None
