from enum import IntEnum, auto

from config.global_config import suffix

UPLOAD_FILES = True

files_to_upload_dir = f"files_to_upload{suffix}"

n_hashes = 10
split_size = 2**11
media_split_size = 2**18


class PeerType(IntEnum):
    UNKNOWN = auto()
    MYSELF = auto()
    CLIENT = auto()
    SERVER = auto()


globals().update({
    f"{PeerType.__name__.upper()}_{pt_name}": ptype.value
    for pt_name, ptype in PeerType.__members__.items()
})
