from lib.services.configuration.configuration import ConfigurationService
from lib.services.configuration.interface.config_service import ConfigServiceInterface
from lib.services.configuration.interface.configuration_type import ConfigurationTypeInterface


class QueryNotFoundError(LookupError):
    pass


class QueryConfiguration(ConfigurationTypeInterface):
    name: str
    type: str

    def __init__(self, name: str, type: str, **kwargs: object) -> None:
        self.name = name
        self.type = type
        self.__dict__.update(kwargs)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class QueryConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("queries", QueryConfiguration)

    def add(self, configuration: QueryConfiguration) -> QueryConfiguration:  # type: ignore[override]
        return self._config.add(configuration)  # type: ignore[return-value]

    def list(self, name: str = "name") -> list[QueryConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> QueryConfiguration:  # type: ignore[override]
        try:
            return self._config.get_one(name)  # type: ignore[return-value]
        except KeyError:
            raise QueryNotFoundError(name)

    def update(self, name: str, updates: dict) -> QueryConfiguration:  # type: ignore[override]
        updates.pop('type', None)
        try:
            return self._config.update(name, updates)  # type: ignore[return-value]
        except KeyError:
            raise QueryNotFoundError(name)

    def remove(self, name: str) -> str:
        try:
            return self._config.remove(name)
        except KeyError:
            raise QueryNotFoundError(name)
