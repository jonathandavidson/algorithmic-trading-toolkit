from abc import ABC, abstractmethod

from lib.models.historical_bars import BaseModel


class DatasourceAdapterInterface(ABC):

    @abstractmethod
    def convert_to_model(self, data: dict) -> BaseModel: ...

    @abstractmethod
    def fetch_rows(self) -> list[BaseModel]: ...

    @abstractmethod
    def test_connection(self) -> bool: ...
