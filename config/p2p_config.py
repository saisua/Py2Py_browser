from enum import IntEnum, auto
import os

from config.global_config import suffix

UPLOAD_FILES = os.getenv(
	"P2Py_UPLOAD_FILES",
	"true"
).lower().strip() == "true"

files_to_upload_dir = os.getenv(
	"P2Py_DIR_TO_UPLOAD",
	f"files_to_upload{suffix}"
)

n_hashes = int(os.getenv(
	"P2Py_NUM_HASHES",
	'10'
))
split_size = 2**os.getenv(
	"P2Py_SPLIT_SIZE",
	11
)
media_split_size = 2**os.getenv(
	"P2Py_MEDIA_SPLIT_SIZE",
	18
)


class PeerType(IntEnum):
    UNKNOWN = auto()
    MYSELF = auto()
    CLIENT = auto()
    SERVER = auto()


globals().update({
    f"{PeerType.__name__.upper()}_{pt_name}": ptype.value
    for pt_name, ptype in PeerType.__members__.items()
})
