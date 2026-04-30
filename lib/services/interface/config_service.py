from abc import ABC, abstractmethod


class ConfigServiceInterface(ABC):

    @abstractmethod
    def add(self, name: str, configuration: dict) -> dict: ...

    @abstractmethod
    def list(self, name: str) -> list[dict]: ...

    @abstractmethod
    def remove(self, name: str) -> str: ...

    @abstractmethod
    def get_one(self, name: str) -> dict: ...
