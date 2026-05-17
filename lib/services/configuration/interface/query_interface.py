from abc import abstractmethod
from typing import ClassVar

from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


class QueryInterface(ConfigurationTypeInterface):
    name: ClassVar[str]

    @abstractmethod
    def to_dict(self) -> dict: ...
