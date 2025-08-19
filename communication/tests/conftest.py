# communication/tests/conftest.py
import pytest
from communication.communication import Communication
from communication.concurrency_layers import ThreadLayer


@pytest.fixture
def communication():
    return Communication()


@pytest.fixture
def thread_layer():
    return ThreadLayer(1)
