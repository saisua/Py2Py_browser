from .main_thread import MainThreadLayer
from .thread import ThreadLayer
from .process import ProcessLayer


concurrency_layer_t = (
    MainThreadLayer |
    ThreadLayer |
    ProcessLayer
)
