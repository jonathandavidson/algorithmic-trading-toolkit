from lib.services.configuration.collection import CollectionConfiguration, DatabaseNotFoundError, DatasourceNotFoundError
from lib.services.configuration.database import DatabaseConfigurationService, DatabaseConfiguration
from lib.services.configuration.datasource import DatasourceConfigurationService, DatasourceConfiguration
from lib.adapters.database_adapter import DatabaseAdapter
from lib.adapters.datasource_adapter import DatasourceAdapter
from lib.orchestrators.collection_orchestrator import CollectionOrchestrator


class CollectionRunnerService:

    _collection_orchestrator: CollectionOrchestrator

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

        self._collection_orchestrator = self._build_collection_orchestrator(database_config, datasource_config)

    def _build_collection_orchestrator(self, database_config: DatabaseConfiguration, datasource_config: DatasourceConfiguration) -> CollectionOrchestrator:
        db_adapter = DatabaseAdapter(database_config)
        datasource_adapter = DatasourceAdapter(datasource_config)
        return CollectionOrchestrator(db_adapter, datasource_adapter)

    def init_collection(self) -> str:
        self._collection_orchestrator.init_collection()
        return self._collection_config.name

    def run_collection(self) -> int:
        return self._collection_orchestrator.run_collection()
    
    def test_connections(self) -> str:
        self._collection_orchestrator._datasource_adapter.test_connection()
        self._collection_orchestrator._db_adapter.test_connection()
        return self._collection_config.name
