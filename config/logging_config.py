import logging

logging_level = logging.WARNING

logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging_level)
aiosqlite_logger = logging.getLogger('aiosqlite')
aiosqlite_logger.setLevel(logging_level)
