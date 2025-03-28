from communication.concurrency_layers.thread import ThreadLayer


class MainThreadLayer(ThreadLayer):
    __slots__ = ()

    def __init__(self):
        super().__init__(0)
