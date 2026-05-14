from lib.adapters.factory.datasource_adapter_factory import DatasourceAdapterFactory
from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.type.datasource_configuration import DatasourceConfiguration
from lib.utils.crypto import decrypt_secret, encrypt_secret


class DatasourceConfigurationService(DatasourceConfiguration):

    def __init__(self) -> None:
        self._config = ConfigurationService("datasources", DatasourceConfiguration)

    def add(self, configuration: DatasourceConfiguration) -> DatasourceConfiguration:  # type: ignore[override]
        encrypted = DatasourceConfiguration(
            name=configuration.name,
            type=configuration.type,
            api_key=configuration.api_key,
            api_secret=encrypt_secret(configuration.api_secret),
        )
        self._config.add(encrypted)
        return configuration

    def list(self, name: str = "name") -> list[DatasourceConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> DatasourceConfiguration:  # type: ignore[override]
        entry = self._config.get_one(name)  # type: ignore[assignment]
        return DatasourceConfiguration(
            name=entry.name,
            type=entry.type,
            api_key=entry.api_key,
            api_secret=decrypt_secret(entry.api_secret),
        )

    def update(self, name: str, updates: dict) -> DatasourceConfiguration:  # type: ignore[override]
        encrypted = dict(updates)
        if "api_secret" in encrypted:
            encrypted["api_secret"] = encrypt_secret(encrypted["api_secret"])
        return self._config.update(name, encrypted)  # type: ignore[return-value]

    def remove(self, name: str) -> str:
        return self._config.remove(name)

    def test(self, name: str) -> str:
        datasource = self.get_one(name)
        datasource_adapter = DatasourceAdapterFactory.create_adapter(datasource)
        datasource_adapter.test_connection()
        return name
