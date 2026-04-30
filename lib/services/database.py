from lib.services.configuration import ConfigurationService
from lib.utils.database import connect

_config = ConfigurationService()

_TYPE = "databases"


def add(name: str, db_type: str, username: str, password: str, host: str, port: int, dbname: str) -> dict:
    is_first = len(_config.list(_TYPE, "name")) == 0
    entry = {
        "name": name,
        "type": db_type,
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname,
    }
    if is_first:
        entry["default"] = True
    return _config.add(_TYPE, name, entry)


def list() -> list[dict]:
    return _config.list(_TYPE, "name")


def remove(name: str) -> str:
    return _config.remove(_TYPE, name)


def test(name: str) -> str:
    databases = _config.list(_TYPE, "name")
    db = next((d for d in databases if d["name"] == name), None)
    if db is None:
        raise KeyError(name)
    with connect(db):
        pass
    return name
