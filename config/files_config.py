import os

from config.global_config import suffix

data_path = os.getenv(
	"P2Py_FILES_DATA_PATH",
	"data"
)

hashes_dir = os.getenv(
	"P2Py_FILES_HASH_DIR",
	os.path.join(data_path, f"hashes{suffix}")
)
data_dir = os.getenv(
	"P2Py_FILES_DATA_DIR",
	os.path.join(data_path, f"data{suffix}")
)
chat_dir = os.getenv(
	"P2Py_FILES_CHAT",
	os.path.join(data_path, f"chat{suffix}")
)
supported_video_extensions = [
	# ".mp4",
	# ".mkv",
	# ".avi",
	# ".mov",
	# ".wmv",
	# ".flv",
	".webm",
]
supported_audio_extensions = [
	# ".mp3",
	# ".wav",
	# ".ogg",
	".m4a",
	".aac",
	# ".flac",
	# ".wma",
	".weba",
]
