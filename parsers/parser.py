from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def parse(self, dir_path: str):
        raise NotImplementedError(f"Function `parse` is not implemented for: {self.__class__.__name__}")
