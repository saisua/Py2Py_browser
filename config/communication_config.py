from enum import IntEnum, auto


class CommunicationUserIds(IntEnum):
    BROWSER_ID = auto()
    SERVER_ID = auto()
    SOCIAL_ID = auto()


globals().update({
    id_k: id_v.value
    for id_k, id_v in CommunicationUserIds.__members__.items()
})
