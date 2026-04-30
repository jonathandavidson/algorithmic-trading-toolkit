from dataclasses import dataclass

import requests

from lib.services.configuration import ConfigurationService
from lib.services.interface.config_service import ConfigServiceInterface
from lib.services.interface.configuration_type import ConfigurationTypeInterface

_TEST_URLS = {
    "alpaca": "https://data.alpaca.markets/v1beta3/crypto/us/bars",
}


@dataclass
class DatasourceConfiguration(ConfigurationTypeInterface):
    name: str
    type: str
    api_key: str
    api_secret: str


class DatasourceConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("datasources", DatasourceConfiguration)

    def add(self, configuration: DatasourceConfiguration) -> DatasourceConfiguration:  # type: ignore[override]
        return self._config.add(configuration)  # type: ignore[return-value]

    def list(self, name: str = "name") -> list[DatasourceConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> DatasourceConfiguration:  # type: ignore[override]
        return self._config.get_one(name)  # type: ignore[return-value]

    def remove(self, name: str) -> str:
        return self._config.remove(name)

    def test(self, name: str) -> str:
        datasources = self._config.list("name")
        ds = next((d for d in datasources if d.name == name), None)
        if ds is None:
            raise KeyError(name)
        url = _TEST_URLS[ds.type]
        response = requests.get(
            url,
            auth=(ds.api_key, ds.api_secret),
            headers={"accept": "application/json"},
            params={"symbols": "BTC/USD", "timeframe": "1D"},
        )
        response.raise_for_status()
        return name
