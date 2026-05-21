from lib.adapters.database_adapter import DatabaseAdapter, DatabaseInsertError
from lib.adapters.interfaces.datasource_adapter_interface import DatasourceAdapterInterface

from lib.services.configuration.collection import CollectionConfiguration, DatabaseNotFoundError, DatasourceNotFoundError, QueryNotFoundError
from lib.services.configuration.database import DatabaseConfigurationService
from lib.services.configuration.datasource import DatasourceConfigurationService
from lib.services.configuration.query import QueryConfiguration, QueryConfigurationService
from lib.services.configuration.query import QueryNotFoundError as _QueryServiceNotFoundError
from lib.adapters.database_adapter import DatabaseAdapter
from lib.adapters.factory.datasource_adapter_factory import DatasourceAdapterFactory


class DatasourceFetchError(Exception):
    pass


class CollectionOrchestrator:

    _db_adapter: DatabaseAdapter
    _datasource_adapter: DatasourceAdapterInterface
    _query_config: QueryConfiguration | None

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

        self._query_config = None
        if collection_config.query is not None:
            try:
                self._query_config = QueryConfigurationService().get_one(collection_config.query)
            except _QueryServiceNotFoundError as e:
                raise QueryNotFoundError(str(e)) from e

        self._db_adapter = DatabaseAdapter.get_instance(database_config)
        self._datasource_adapter = DatasourceAdapterFactory.create_adapter(datasource_config)

    def init_collection(self) -> None:
        if self._query_config is None:
            raise ValueError("Cannot initialize collection: no query configuration is set.")
        model = self._datasource_adapter.get_model(self._query_config)
        self._db_adapter.init_model(model)

    def run_collection(self) -> int:
        total: int = 0
        try:
            for rows in self._datasource_adapter.run_query(self._query_config):
                try:
                    self._db_adapter.insert_rows(rows)
                except Exception as e:
                    raise DatabaseInsertError(str(e)) from e
                total += len(rows)
        except DatabaseInsertError:
            raise
        except Exception as e:
            raise DatasourceFetchError('Error fetching from data source: ' + str(e)) from e
        return total
