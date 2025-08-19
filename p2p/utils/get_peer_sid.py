from sqlalchemy import select

from config import PEERTYPE_MYSELF

from db.models.peers import Peers

from db.utils.execute import _session_execute


async def get_peer_sid(
        session_maker,
        addr: bytes | None = None,
) -> int:
    if addr is None:
        cond = Peers.type == PEERTYPE_MYSELF
    else:
        cond = Peers.address == addr

    return await _session_execute(
        session_maker,
        select(Peers.sid).where(cond),
        scalar=True,
    )
