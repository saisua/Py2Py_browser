import os

from config.global_config import suffix
from config.files_config import data_path

db_protocol = "sqlite+aiosqlite"
db_dir = os.path.join(data_path, f"data{suffix}.db")
