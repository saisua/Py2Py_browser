from abc import abstractmethod


class Request:
    CODE: int

    @abstractmethod
    def handle(self, request, *args, **kwargs):
        ...

    @staticmethod
    @abstractmethod
    def send(
        session_maker,
        addr,
        sid,
        *args,
        own_sid: int | None = None,
        **kwargs,
    ):
        ...
