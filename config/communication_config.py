from enum import IntEnum, auto


class CommunicationUserIds(IntEnum):
    BROWSER_ID = auto()
    SERVER_ID = auto()
    SOCIAL_ID = auto()


globals().update(CommunicationUserIds.__members__)
