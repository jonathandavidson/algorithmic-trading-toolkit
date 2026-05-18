from abc import ABC, abstractmethod
from collections.abc import Generator

from lib.models.historical_bars import BaseModel
from lib.services.configuration.interface.query_interface import QueryInterface


class DatasourceQueryInterface(ABC):

    @abstractmethod
    def fetch_rows(self, query_config: QueryInterface) -> Generator[list[BaseModel], None, None]: ...
