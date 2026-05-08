from lib.services.configuration.type.datasource_configuration import DatasourceConfiguration
from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface


class DatasourceNotFoundError(LookupError):
    pass


class DatasourceAdapterFactory:
    @staticmethod
    def create_adapter(datasource_config: DatasourceConfiguration) -> DatasourceAdapterInterface:
        if datasource_config.type == 'alpaca':
            from lib.adapters.datasource.alpaca_datasource_adapter import AlpacaDatasourceAdapter
            return AlpacaDatasourceAdapter(datasource_config)
        else:
            raise DatasourceNotFoundError(f"Datasource type '{datasource_config}' not found")
