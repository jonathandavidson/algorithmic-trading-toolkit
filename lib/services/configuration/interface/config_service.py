from abc import ABC, abstractmethod

from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


class ConfigServiceInterface(ABC):

    @abstractmethod
    def add(self, configuration: ConfigurationTypeInterface) -> ConfigurationTypeInterface: ...

    @abstractmethod
    def list(self, name: str) -> list[ConfigurationTypeInterface]: ...

    @abstractmethod
    def remove(self, name: str) -> str: ...

    @abstractmethod
    def get_one(self, name: str) -> ConfigurationTypeInterface: ...

    @abstractmethod
    def update(self, name: str, updates: dict) -> ConfigurationTypeInterface: ...
