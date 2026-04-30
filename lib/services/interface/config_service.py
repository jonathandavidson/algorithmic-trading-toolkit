from abc import ABC, abstractmethod

from lib.services.interface.configuration_type import ConfigurationTypeInterface


class ConfigServiceInterface(ABC):

    @abstractmethod
    def add(self, configuration: ConfigurationTypeInterface) -> ConfigurationTypeInterface: ...

    @abstractmethod
    def list(self, name: str) -> list[ConfigurationTypeInterface]: ...

    @abstractmethod
    def remove(self, name: str) -> str: ...

    @abstractmethod
    def get_one(self, name: str) -> ConfigurationTypeInterface: ...
