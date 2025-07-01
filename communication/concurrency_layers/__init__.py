from .main_thread import MainThreadLayer
from .thread import ThreadLayer
from .process import ProcessLayer


concurrency_layer_t = (
    MainThreadLayer |  # noqa: W504
    ThreadLayer |  # noqa: W504
    ProcessLayer
)
