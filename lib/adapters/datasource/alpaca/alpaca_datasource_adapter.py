from collections.abc import Generator

from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface
from lib.models.alpaca.historical_bar import AlpacaHistoricalBar
from lib.models.base import BaseModel
from lib.services.configuration.datasource import DatasourceConfiguration
from lib.services.configuration.query import QueryConfiguration
from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
from lib.services.datasources.alpaca.alpaca_service import AlpacaService


class AlpacaDatasourceAdapter(DatasourceAdapterInterface):
    def __init__(self, config: DatasourceConfiguration) -> None:
        self._config = config
        self._service = AlpacaService(config)

    def get_model(self, query_config: QueryConfiguration) -> type[BaseModel]:
        if query_config.type == 'historical-bars':
            return AlpacaHistoricalBar
        raise ValueError(f"Unsupported query type: {query_config.type}")

    def run_query(self, query_config: QueryConfiguration) -> Generator[list[AlpacaHistoricalBar], None, None]:
        if query_config.type == 'historical-bars':
            fields = {k: v for k, v in query_config.to_dict().items() if k not in ('name', 'type')}
            return self._service.fetch_historical_bars(HistoricalBarsQueryType(**fields))
        raise ValueError(f"Unsupported query type: {query_config.type}")

    def test_connection(self) -> bool:
        return self._service.test_connection()
