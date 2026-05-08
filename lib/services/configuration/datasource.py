from lib.adapters.factory.datasource_adapter_factory import DatasourceAdapterFactory
from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.type.datasource_configuration import DatasourceConfiguration


class DatasourceConfigurationService(DatasourceConfiguration):

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
        datasource = self.get_one(name)
        datasource_adapter = DatasourceAdapterFactory.create_adapter(datasource)
        datasource_adapter.test_connection()
        return name
