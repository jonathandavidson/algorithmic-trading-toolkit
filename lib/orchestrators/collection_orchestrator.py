from lib.adapters.database_adapter import DatabaseAdapter, DatabaseInsertError
from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface
from lib.models.historical_bars import BaseModel
from lib.services.configuration.collection import CollectionConfiguration, DatabaseNotFoundError, DatasourceNotFoundError
from lib.services.configuration.database import DatabaseConfigurationService
from lib.services.configuration.datasource import DatasourceConfigurationService
from lib.adapters.database_adapter import DatabaseAdapter
from lib.adapters.factory.datasource_adapter_factory import DatasourceAdapterFactory


class DatasourceFetchError(Exception):
    pass


class CollectionOrchestrator:

    _db_adapter: DatabaseAdapter
    _datasource_adapter: DatasourceAdapterInterface

    def __init__(self, collection_config: CollectionConfiguration):
        self._collection_config = collection_config

        try:
            database_config = DatabaseConfigurationService().get_one(collection_config.database)
        except KeyError as e:
            raise DatabaseNotFoundError(e.args[0]) from e

        try:
            datasource_config = DatasourceConfigurationService().get_one(collection_config.datasource)
        except KeyError as e:
            raise DatasourceNotFoundError(e.args[0]) from e

        self._db_adapter = DatabaseAdapter.get_instance(database_config)
        self._datasource_adapter = DatasourceAdapterFactory.create_adapter(datasource_config)

    def init_collection(self) -> None:
        self._db_adapter.init_database()

    def run_collection(self) -> int:
        try:
            rows: list[BaseModel] = self._datasource_adapter.fetch_rows(self._collection_config)
        except Exception as e:
            raise DatasourceFetchError('Error fetching from data source: ' + str(e)) from e
        try:
            self._db_adapter.insert_rows(rows)
        except Exception as e:
            raise DatabaseInsertError(str(e)) from e
        return len(rows)
