from abc import ABC, abstractmethod
from collections.abc import Generator

from lib.models.historical_bars import BaseModel
from lib.services.configuration.query import QueryConfiguration


class DatasourceAdapterInterface(ABC):

    @abstractmethod
    def convert_to_model(self, data: dict) -> BaseModel: ...

    @abstractmethod
    def run_query(self, query_config: QueryConfiguration) -> Generator[list[BaseModel], None, None]: ...

    @abstractmethod
    def test_connection(self) -> bool: ...
