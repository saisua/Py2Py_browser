import ipaddress


def addr_to_bytes(addr: str, port: int | str | None = None) -> bytes:
    ip = ipaddress.ip_address(addr).packed
    if port:
        if not isinstance(port, int):
            port = int(port)
        ip += port.to_bytes(2, 'big')
    return ip
