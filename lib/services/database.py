import dataclasses
from dataclasses import dataclass

from lib.services.configuration import ConfigurationService
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


_config = ConfigurationService("databases", DatabaseConfiguration)


def add(configuration: DatabaseConfiguration) -> DatabaseConfiguration:
    is_first = len(_config.list("name")) == 0
    if is_first:
        configuration = dataclasses.replace(configuration, default=True)
    return _config.add(configuration)  # type: ignore[return-value]


def list() -> list[DatabaseConfiguration]:
    return _config.list("name")  # type: ignore[return-value]


def remove(name: str) -> str:
    return _config.remove(name)


def test(name: str) -> str:
    databases = _config.list("name")
    db = next((d for d in databases if d.name == name), None)
    if db is None:
        raise KeyError(name)
    with connect(db.to_dict()):
        pass
    return name
