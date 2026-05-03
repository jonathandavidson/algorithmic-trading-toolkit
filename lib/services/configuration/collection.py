import dataclasses
from dataclasses import dataclass

from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.interface.config_service import ConfigServiceInterface
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


class CollectionNotFoundError(LookupError):
    pass


class DatabaseNotFoundError(LookupError):
    pass


class DatasourceNotFoundError(LookupError):
    pass


@dataclass
class CollectionConfiguration(ConfigurationTypeInterface):
    name: str
    database: str
    type: str
    start: str
    datasource: str | None = None
    frequency: str | None = None
    end: str | None = None

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        if d["datasource"] is None:
            del d["datasource"]
        if d["frequency"] is None:
            del d["frequency"]
        if d["end"] is None:
            del d["end"]
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
