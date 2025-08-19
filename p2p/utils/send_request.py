import asyncio
import bson
import logging

from config import logger

from encryption.encrypt_message import encrypt_message
from encryption.decrypt_message import decrypt_message

from p2p.utils.addr_to_str import addr_to_str
from p2p.utils.get_peer_sid import get_peer_sid


async def send_request(
    session_maker,
    addr,
    sid,
    request,
    *,
    large_response=False,
    own_sid: int | None = None,
):
    (addr_str, port) = addr_to_str(addr)

    logging.error(f"###\n### Sending msg to {addr_str}:{port}\n###")

    try:
        reader, writer = await asyncio.open_connection(
            addr_str,
            port,
        )
    except Exception:
        if logger.isEnabledFor(logging.WARNING):
            logger.warning(f"address {addr_str}:{port} is not available")
        return None

    if logger.isEnabledFor(logging.INFO):
        logger.info(f"Sending request to {addr_str}:{port}")

    bson_req = bson.dumps(request)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Encrypting {len(bson_req)} bytes: {bson_req}")

    encrypted_req = await encrypt_message(session_maker, bson_req, sid)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Sending {len(encrypted_req)} bytes: {encrypted_req}")

    if own_sid is None:
        own_sid = await get_peer_sid(session_maker)

    first_payload = (
        own_sid.to_bytes(4, 'big')
        +  # noqa: W504 W503
        len(encrypted_req).to_bytes(4, 'big')
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Sending {len(first_payload)} bytes: {first_payload}")

    writer.write(first_payload)
    await writer.drain()

    new_port = await reader.read(4)
    if not new_port:
        logging.error(f"No new port for {len(encrypted_req)} bytes")
        writer.close()
        return None

    new_port = int.from_bytes(new_port, 'big')

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Redirected to {new_port}")

    limit = 2**32 if large_response else 2**16
    try:
        reader2, writer2 = await asyncio.open_connection(
            addr_str,
            new_port,
            limit=limit,
        )
    except Exception:
        logging.error(f"address {addr_str}:{new_port} is not available")
        return None
    finally:
        writer.close()

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Sending {len(encrypted_req)} bytes: {encrypted_req}")

    writer2.write(encrypted_req)
    await writer2.drain()

    res_len = int.from_bytes(await reader2.read(4), 'big')

    if res_len > limit:
        logging.error("Response is too large")
        writer2.close()
        return None

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Receiving {res_len} bytes")

    encrypted_res = b""
    while len(encrypted_res) < res_len:
        encrypted_res += await reader2.read(res_len - len(encrypted_res))

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Received {len(encrypted_res)} bytes: {encrypted_res}")

    res = await decrypt_message(session_maker, encrypted_res, sid)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Decrypted {len(res)} bytes: {res}")

    try:
        return bson.loads(res)
    except Exception:
        logging.error("Error loading bson response")
        return None
    finally:
        writer2.close()
        await writer.wait_closed()
        await writer2.wait_closed()
