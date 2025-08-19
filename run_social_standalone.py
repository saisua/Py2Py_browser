from config import (
    DEBUG_PURGE_DATA,
    SOCIAL_ID,
    SERVER_ID,
)

if DEBUG_PURGE_DATA:
    from debugging.purge_data import purge_data
    purge_data()

from db import session_maker

from communication.communication import Communication
from communication.concurrency_layers import MainThreadLayer, ThreadLayer

from social.social import SocialApp

from p2p.server import AsyncBsonServer


# if DEBUG_ADD_PEERS:
#     from debugging.add_peers import add_peers
#     from debugging.add_groups import add_groups

#     add_peers(session_maker)
#     if DEBUG_ADD_GROUPS:
#         add_groups(session_maker)

if __name__ == '__main__':
    comm = Communication()

    server_user = comm.add_user(SERVER_ID, ThreadLayer(1))
    server = AsyncBsonServer(session_maker, server_user)
    server.start()

    social_user = comm.add_user(SOCIAL_ID, MainThreadLayer())
    try:
        SocialApp(session_maker, social_user).run()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
