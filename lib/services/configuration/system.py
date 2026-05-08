import dataclasses
from dataclasses import dataclass

from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


@dataclass
class SystemConfiguration(ConfigurationTypeInterface):

    name: str = 'global'

    def __init__(self, name, **kwds):
        self.name = name
        self.__dict__.update(kwds)

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d


class SystemConfigurationService():

    def __init__(self, type='global') -> None:
        self._config = ConfigurationService(type, SystemConfiguration, 'system')

    def get_one(self, name: str) -> ConfigurationTypeInterface:  # type: ignore[override]
        return self._config.get_one(name)  # type: ignore[return-value]
