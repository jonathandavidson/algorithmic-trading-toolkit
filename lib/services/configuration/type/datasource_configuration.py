from dataclasses import dataclass

from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface

@dataclass
class DatasourceConfiguration(ConfigurationTypeInterface):
    name: str
    type: str
    api_key: str
    api_secret: str
