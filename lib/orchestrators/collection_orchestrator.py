from lib.adapters.database_adapter import DatabaseAdapter
from lib.adapters.datasource_adapter import DatasourceAdapter
from lib.models.historical_bars import HistoricalBar


class CollectionOrchestrator:

    _db_adapter: DatabaseAdapter
    _datasource_adapter: DatasourceAdapter

    def __init__(self, db_adapter: DatabaseAdapter, datasource_adapter: DatasourceAdapter):
        self._db_adapter = db_adapter
        self._datasource_adapter = datasource_adapter

    def init_collection(self):
        self._db_adapter.init_database()

    def run_collection(self) -> int:
        bars: HistoricalBar = self._datasource_adapter.fetch_historical_bars()
        self._db_adapter.insert_historical_bars(bars)
        return len(bars)
