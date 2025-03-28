import ipaddress


def addr_to_str(addr: bytes) -> str:
    if len(addr) == 4 or len(addr) == 16:
        return (ipaddress.ip_address(addr).compressed, None)
    elif len(addr) == 6 or len(addr) == 18:
        ip = ipaddress.ip_address(addr[:-2]).compressed
        port = int.from_bytes(addr[-2:], 'big')
        return (ip, port)
    raise ValueError(f'Invalid address length: {len(addr)}')
