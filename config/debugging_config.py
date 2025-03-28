import os

from config.files_config import data_path

DEBUG_PURGE_DATA = False
DEBUG_SHARE_BUNDLE = True
DEBUG_ADD_PEERS = True
DEBUG_REMOVE_PREV_PEERS = True
DEBUG_ADD_GROUPS = True
DEBUG_DISABLE_ENCRYPTION = True

peer_addr_dir = os.path.join(data_path, "peers")
