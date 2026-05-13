from abc import ABC, abstractmethod
from collections.abc import Generator

from lib.models.historical_bars import BaseModel
from lib.services.configuration.collection import CollectionConfiguration


class DatasourceAdapterInterface(ABC):

    @abstractmethod
    def convert_to_model(self, data: dict) -> BaseModel: ...

    @abstractmethod
    def fetch_rows(self, collection_config: CollectionConfiguration) -> Generator[list[BaseModel], None, None]: ...

    @abstractmethod
    def test_connection(self) -> bool: ...
