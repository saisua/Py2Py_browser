import asyncio
import bson
import logging

from encryption.encrypt_message import encrypt_message
from encryption.decrypt_message import decrypt_message

from p2p.utils.addr_to_str import addr_to_str


async def send_request(
    session_maker,
    addr,
    sid,
    request,
    *,
    large_response=False,
):
    (addr_str, port) = addr_to_str(addr)

    logging.info(f"Sending request to {addr_str}:{port}")

    bson_req = bson.dumps(request)
    encrypted_req = await encrypt_message(session_maker, bson_req, sid)

    try:
        reader, writer = await asyncio.open_connection(
            addr_str,
            port,
        )
    except Exception:
        logging.error(f"address {addr_str}:{port} is not available")
        return None

    logging.debug(f"Sending {len(encrypted_req)} bytes")

    first_payload = (
        sid.to_bytes(4, 'big') +
        len(encrypted_req).to_bytes(4, 'big')
    )

    writer.write(first_payload)
    await writer.drain()

    new_port = await reader.read(4)
    if not new_port:
        logging.error("No new port")
        return None

    new_port = int.from_bytes(new_port, 'big')
    logging.debug(f"Redirected to {new_port}")

    limit = 2**32 if large_response else 2**16
    try:
        reader, writer = await asyncio.open_connection(
            addr_str,
            new_port,
            limit=limit,
        )
    except Exception:
        logging.error(f"address {addr_str}:{new_port} is not available")
        return None

    writer.write(encrypted_req)
    await writer.drain()

    res_len = int.from_bytes(await reader.read(4), 'big')

    if res_len > limit:
        logging.error("Response is too large")
        # return None

    logging.debug(f"Receiving {res_len} bytes")

    encrypted_res = b""
    while len(encrypted_res) < res_len:
        encrypted_res += await reader.read(res_len - len(encrypted_res))

    res = await decrypt_message(session_maker, encrypted_res, sid)

    try:
        return bson.loads(res)
    except Exception:
        logging.error("Error loading bson response")
        return None
