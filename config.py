import os

# To launch multiple instances, set SUFFIX to a unique string
suffix = os.getenv("SUFFIX", "")


DEBUG_PURGE_DATA = True
DEBUG_ADD_PEER = True

UPLOAD_FILES = False

init_pages = [
    "https://www.duckduckgo.com",
]

data_path = "data"

hashes_dir = os.path.join(data_path, f"hashes{suffix}")
data_dir = os.path.join(data_path, f"data{suffix}")

n_hashes = 10
split_size = 2**11

db_protocol = "sqlite+aiosqlite"
db_dir = os.path.join(data_path, f"data{suffix}.db")

files_to_upload_dir = "files_to_upload"

static_salt = b'2\x8bd\x01z\xc9\xf9\x95]\xe2\x13\xfc\xda\x80\x0c\xd7'
assert len(static_salt) == 16

num_threads = 25
