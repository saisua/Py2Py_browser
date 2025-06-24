import os

from config.global_config import suffix

data_path = "data"

hashes_dir = os.path.join(data_path, f"hashes{suffix}")
data_dir = os.path.join(data_path, f"data{suffix}")
chat_dir = os.path.join(data_path, f"chat{suffix}")
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
