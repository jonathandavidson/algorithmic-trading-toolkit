from lib.adapters.database_adapter import DatabaseAdapter, DatabaseInsertError
from lib.adapters.datasource_adapter import DatasourceAdapter, DatasourceFetchError
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
        try:
            bars: HistoricalBar = self._datasource_adapter.fetch_historical_bars()
        except Exception as e:
            raise DatasourceFetchError('Error fetching from data source: ' + str(e)) from e
        try:
            self._db_adapter.insert_historical_bars(bars)
        except Exception as e:
            raise DatabaseInsertError(str(e)) from e
        return len(bars)
