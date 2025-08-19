import os
import pytest

from config import db_dir

from p2p.utils.addr_to_bytes import addr_to_bytes


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield  # Tests run here

    if os.path.isfile(db_dir):
        os.remove(db_dir)


addr1 = addr_to_bytes("::1", 12412)
addr2 = addr_to_bytes("::1", 12413)
