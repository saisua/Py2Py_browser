import os

from config.global_config import DEVELOPMENT

from config.files_config import data_path

if DEVELOPMENT:
	DEBUG_PURGE_DATA = os.getenv(
		"P2Py_DEBUG_PURGE_DATA",
		"false"
	).lower().strip() == 'true'
	DEBUG_SHARE_BUNDLE = os.getenv(
		"P2Py_DEBUG_SHARE_BUNDLE",
		"true",
	).lower().strip() == 'true'
	DEBUG_ADD_PEERS = os.getenv(
		"P2Py_DEBUG_ADD_PEERS",
		"true",
	).lower().strip() == 'true'
	DEBUG_REMOVE_PREV_PEERS = os.getenv(
		"P2Py_DEBUG_REMOVE_PREV_PEERS",
		"true",
	).lower().strip() == 'true'
	DEBUG_ADD_GROUPS = os.getenv(
		"P2Py_DEBUG_ADD_GROUPS",
		"false",
	).lower().strip() == 'true'
	DEBUG_DISABLE_ENCRYPTION = os.getenv(
		"P2Py_DEBUG_DISABLE_ENCRYPTION",
		"false",
	).lower().strip() == 'true'
	DEBUG_DISABLE_DISK_REQUESTS = os.getenv(
		"P2Py_DEBUG_DISABLE_DISK_REQUESTS",
		"false",
	).lower().strip() == 'true'
	DEBUG_DISABLE_UPLOAD_MEDIA_DATA = os.getenv(
		"P2Py_DEBUG_DISABLE_UPLOAD_MEDIA_DATA",
		"true",
	).lower().strip() == 'true'
	DEBUG_DISABLE_COMMUNICATION = os.getenv(
		"P2Py_DEBUG_DISABLE_COMMUNICATION",
		"false",
	).lower().strip() == 'true'
	DEBUG_DISABLE_PEER_REQUESTS = os.getenv(
		"P2Py_DEBUG_DISABLE_PEER_REQUESTS",
		"false",
	).lower().strip() == 'true'
	DEBUG_RESOLVE_REQUESTS_SEQUENTIALLY = os.getenv(
		"P2Py_DEBUG_RESOLVE_REQUESTS_SEQUENTIALLY",
		"false",
	).lower().strip() == 'true'
else:
	DEBUG_PURGE_DATA = False
	DEBUG_SHARE_BUNDLE = False
	DEBUG_ADD_PEERS = False
	DEBUG_REMOVE_PREV_PEERS = False
	DEBUG_ADD_GROUPS = False
	DEBUG_DISABLE_ENCRYPTION = False
	DEBUG_DISABLE_DISK_REQUESTS = False
	DEBUG_DISABLE_UPLOAD_MEDIA_DATA = False
	DEBUG_DISABLE_COMMUNICATION = False
	DEBUG_DISABLE_PEER_REQUESTS = False
	DEBUG_RESOLVE_REQUESTS_SEQUENTIALLY = False


peer_addr_dir = os.path.join(data_path, "peers")
