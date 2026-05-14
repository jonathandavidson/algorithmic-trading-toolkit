import dataclasses
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.interface.config_service import ConfigServiceInterface
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


class CollectionNotFoundError(LookupError):
    pass


class DatabaseNotFoundError(LookupError):
    pass


class DatasourceNotFoundError(LookupError):
    pass


class CollectionFrequency(str, Enum):
    ONE_DAY = '1d'
    ONE_MINUTE = '1m'


@dataclass
class CollectionConfiguration(ConfigurationTypeInterface):
    name: str
    database: str
    type: str
    start: datetime
    datasource: str | None = None
    frequency: CollectionFrequency | None = None
    end: datetime | None = None
    symbols: list[str] | None = None

    def __post_init__(self) -> None:
        self.start = self._parse_dt(self.start)
        if self.end is not None:
            self.end = self._parse_dt(self.end)
        if self.frequency is not None and not isinstance(self.frequency, CollectionFrequency):
            self.frequency = CollectionFrequency(self.frequency)

    @staticmethod
    def _parse_dt(value: datetime | str) -> datetime:
        dt = datetime.fromisoformat(value) if isinstance(value, str) else value
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["start"] = self.start.isoformat()
        if d["datasource"] is None:
            del d["datasource"]
        if d["frequency"] is None:
            del d["frequency"]
        else:
            d["frequency"] = self.frequency.value
        if d["end"] is None:
            del d["end"]
        else:
            d["end"] = self.end.isoformat()
        if d["symbols"] is None:
            del d["symbols"]
        return d


class CollectionConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("collections", CollectionConfiguration)

    def _find_collection(self, name: str) -> CollectionConfiguration:
        try:
            return self._config.get_one(name)  # type: ignore[return-value]
        except KeyError:
            raise CollectionNotFoundError(name)

    def add(self, configuration: CollectionConfiguration) -> CollectionConfiguration:  # type: ignore[override]
        return self._config.add(configuration)  # type: ignore[return-value]

    def list(self, name: str = "name") -> list[CollectionConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> CollectionConfiguration:  # type: ignore[override]
        return self._config.get_one(name)  # type: ignore[return-value]

    def update(self, name: str, updates: dict) -> CollectionConfiguration:  # type: ignore[override]
        try:
            return self._config.update(name, updates)  # type: ignore[return-value]
        except KeyError:
            raise CollectionNotFoundError(name)

    def remove(self, name: str) -> str:
        try:
            return self._config.remove(name)
        except KeyError:
            raise CollectionNotFoundError(name)

    def init(self, name: str) -> str:
        from lib.services.collection_runner import CollectionRunnerService
        collection = self._find_collection(name)
        CollectionRunnerService(collection).init_collection()
        return name

    def run(self, name: str) -> int:
        from lib.services.collection_runner import CollectionRunnerService
        collection = self._find_collection(name)
        return CollectionRunnerService(collection).run_collection()
