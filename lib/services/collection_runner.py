from lib.services.configuration.collection import CollectionConfiguration
from lib.orchestrators.collection_orchestrator import CollectionOrchestrator


class CollectionRunnerService:

    _collection_orchestrator: CollectionOrchestrator

    def __init__(self, collection_config: CollectionConfiguration):
        self._collection_config = collection_config
        self._collection_orchestrator = self._build_collection_orchestrator(collection_config)

    def _build_collection_orchestrator(self, collection_config: CollectionConfiguration) -> CollectionOrchestrator:
        return CollectionOrchestrator(collection_config)

    def init_collection(self) -> str:
        self._collection_orchestrator.init_collection()
        return self._collection_config.name

    def run_collection(self) -> int:
        return self._collection_orchestrator.run_collection()
    
    def test_connections(self) -> str:
        self._collection_orchestrator._datasource_adapter.test_connection()
        self._collection_orchestrator._db_adapter.test_connection()
        return self._collection_config.name
