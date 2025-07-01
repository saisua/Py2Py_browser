import os

from config.global_config import suffix
from config.files_config import data_path

db_protocol = "sqlite+aiosqlite"
db_dir = os.getenv(
	"P2Py_DB_URL",
	os.path.join(data_path, f"data{suffix}.db")
)
db_timeout = os.getenv(
	"P2Py_DB_TIMEOUT",
	30
)
db_journal_mode = os.getenv(
	"P2Py_DB_JOURNAL_MODE",
	"WAL"
)
