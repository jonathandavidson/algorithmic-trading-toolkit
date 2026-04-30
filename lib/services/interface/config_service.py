from abc import ABC, abstractmethod


class ConfigServiceInterface(ABC):

    @abstractmethod
    def add(self, type: str, name: str, configuration: dict) -> dict: ...

    @abstractmethod
    def list(self, type: str, name: str) -> list[dict]: ...

    @abstractmethod
    def remove(self, type: str, name: str) -> str: ...
