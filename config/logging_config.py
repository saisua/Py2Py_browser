import logging
import os

from config.global_config import DEVELOPMENT

if DEVELOPMENT:
    logging_level = "DEBUG"
else:
    logging_level = os.getenv(
        "P2Py_LOGGING_LEVEL",
        "WARNING"
    )

logging.basicConfig(level=getattr(logging, logging_level))
logger = logging.getLogger("P2Py_browser")
logger.setLevel(logging_level)
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging_level)
aiosqlite_logger = logging.getLogger('aiosqlite')
aiosqlite_logger.setLevel(logging_level)
