from lib.adapters.database_adapter import DatabaseAdapter, DatabaseInsertError
from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface
from lib.models.historical_bars import BaseModel


class DatasourceFetchError(Exception):
    pass


class CollectionOrchestrator:

    _db_adapter: DatabaseAdapter
    _datasource_adapter: DatasourceAdapterInterface

    def __init__(self, db_adapter: DatabaseAdapter, datasource_adapter: DatasourceAdapterInterface):
        self._db_adapter = db_adapter
        self._datasource_adapter = datasource_adapter

    def init_collection(self):
        self._db_adapter.init_database()

    def run_collection(self) -> int:
        try:
            rows: list[BaseModel] = self._datasource_adapter.fetch_rows()
        except Exception as e:
            raise DatasourceFetchError('Error fetching from data source: ' + str(e)) from e
        try:
            self._db_adapter.insert_rows(rows)
        except Exception as e:
            raise DatabaseInsertError(str(e)) from e
        return len(rows)
