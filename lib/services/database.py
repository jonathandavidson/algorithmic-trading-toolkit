import dataclasses

from dataclasses import dataclass

from lib.services.configuration import ConfigurationService
from lib.services.interface.configuration_type import ConfigurationTypeInterface
from lib.utils.database import connect

_config = ConfigurationService("databases")


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


def add(configuration: DatabaseConfiguration) -> dict:
    is_first = len(_config.list("name")) == 0
    if is_first:
        configuration = dataclasses.replace(configuration, default=True)
    return _config.add(configuration)


def list() -> list[dict]:
    return _config.list("name")


def remove(name: str) -> str:
    return _config.remove(name)


def test(name: str) -> str:
    databases = _config.list("name")
    db = next((d for d in databases if d["name"] == name), None)
    if db is None:
        raise KeyError(name)
    with connect(db):
        pass
    return name
