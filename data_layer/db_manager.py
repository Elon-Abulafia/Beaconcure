from abc import ABC, abstractmethod


class DBManager(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def connect(self):
        raise NotImplementedError(f"Function `connect` is not implemented for: {self.__class__.__name__}")

    @abstractmethod
    def insert(self):
        raise NotImplementedError(f"Function `insert` is not implemented for: {self.__class__.__name__}")

    @abstractmethod
    def find(self):
        raise NotImplementedError(f"Function `find` is not implemented for: {self.__class__.__name__}")

    @abstractmethod
    def update(self):
        raise NotImplementedError(f"Function `update` is not implemented for: {self.__class__.__name__}")

    @abstractmethod
    def delete(self):
        raise NotImplementedError(f"Function `delete` is not implemented for: {self.__class__.__name__}")

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError(f"Function `disconnect` is not implemented for: {self.__class__.__name__}")
