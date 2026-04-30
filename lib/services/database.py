import dataclasses
from dataclasses import dataclass

from lib.services.configuration import ConfigurationService
from lib.services.interface.config_service import ConfigServiceInterface
from lib.services.interface.configuration_type import ConfigurationTypeInterface
from lib.utils.database import connect


@dataclass
class DatabaseConfiguration(ConfigurationTypeInterface):
    name: str
    type: str
    username: str
    password: str
    host: str
    port: int
    dbname: str
    default: bool = False

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        if not d["default"]:
            del d["default"]
        return d


class DatabaseConfigurationService(ConfigServiceInterface):

    def __init__(self) -> None:
        self._config = ConfigurationService("databases", DatabaseConfiguration)

    def add(self, configuration: DatabaseConfiguration) -> DatabaseConfiguration:  # type: ignore[override]
        is_first = len(self._config.list("name")) == 0
        if is_first:
            configuration = dataclasses.replace(configuration, default=True)
        return self._config.add(configuration)  # type: ignore[return-value]

    def list(self, name: str = "name") -> list[DatabaseConfiguration]:  # type: ignore[override]
        return self._config.list(name)  # type: ignore[return-value]

    def get_one(self, name: str) -> DatabaseConfiguration:  # type: ignore[override]
        return self._config.get_one(name)  # type: ignore[return-value]

    def remove(self, name: str) -> str:
        return self._config.remove(name)

    def test(self, name: str) -> str:
        databases = self._config.list("name")
        db = next((d for d in databases if d.name == name), None)
        if db is None:
            raise KeyError(name)
        with connect(db.to_dict()):
            pass
        return name
