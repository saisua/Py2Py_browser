import logging
import os

from config.files_config import data_path
from config.global_config import DEVELOPMENT, suffix

logging_level = os.getenv(
    "P2Py_LOGGING_LEVEL",
    None
)
if DEVELOPMENT and not logging_level:
    logging_level = "DEBUG"
elif not logging_level:
    logging_level = "WARNING"
else:
    logging_level = logging_level.strip().upper()

libraries_logging_level = os.getenv(
    "P2Py_LIBRARIES_LOGGING_LEVEL",
    None
)
if DEVELOPMENT:
    libraries_logging_level = "ERROR"
elif not libraries_logging_level:
    libraries_logging_level = "WARNING"
else:
    libraries_logging_level = libraries_logging_level.strip().upper()

logging_path = os.getenv(
    "P2Py_LOGGING_PATH",
    None
)

if DEVELOPMENT and not logging_path:
    logging_path = os.path.join(data_path, "logs")

logging.basicConfig(level=getattr(logging, logging_level))
logger = logging.getLogger("P2Py_browser")
logger.setLevel(logging_level)

sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(libraries_logging_level)

aiosqlite_logger = logging.getLogger('aiosqlite')
aiosqlite_logger.setLevel(libraries_logging_level)

kivy_logger = logging.getLogger('kivy')
kivy_logger.setLevel(libraries_logging_level)

if logging_path:
    os.makedirs(logging_path, exist_ok=True)

    logger.addHandler(
        logging.FileHandler(
            os.path.join(logging_path, f"p2py{suffix}.log"),
            mode="a",   
        )
    )
    sqlalchemy_logger.addHandler(
        logging.FileHandler(
            os.path.join(logging_path, f"sqlalchemy{suffix}.log"),
            mode="a",
        )
    )
    aiosqlite_logger.addHandler(
        logging.FileHandler(
            os.path.join(logging_path, f"aiosqlite{suffix}.log"),
            mode="a",
        )
    )
    kivy_logger.addHandler(
        logging.FileHandler(
            os.path.join(logging_path, f"kivy{suffix}.log"),
            mode="a",
        )
    )
