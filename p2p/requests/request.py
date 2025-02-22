from abc import abstractmethod


class Request:
    CODE: int

    @abstractmethod
    def handle(self, request, *args, **kwargs):
        ...

    @staticmethod
    @abstractmethod
    def send(
        addr,
        key,
        *args,
        **kwargs,
    ):
        ...
