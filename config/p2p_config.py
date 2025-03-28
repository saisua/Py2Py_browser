from enum import IntEnum, auto

UPLOAD_FILES = False

files_to_upload_dir = "files_to_upload"

n_hashes = 10
split_size = 2**11


class PeerType(IntEnum):
    UNKNOWN = auto()
    MYSELF = auto()
    CLIENT = auto()
    SERVER = auto()


globals().update({
    f"{PeerType.__name__.upper()}_{pt_name}": ptype
    for pt_name, ptype in PeerType.__members__.items()
})
