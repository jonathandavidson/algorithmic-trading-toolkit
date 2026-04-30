import lib.services.configuration as configuration_service
from lib.utils.database import connect

_TYPE = "databases"


def add(name: str, db_type: str, username: str, password: str, host: str, port: int, dbname: str) -> dict:
    is_first = len(configuration_service.list(_TYPE, "name")) == 0
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
    return configuration_service.add(_TYPE, name, entry)


def list() -> list[dict]:
    return configuration_service.list(_TYPE, "name")


def remove(name: str) -> str:
    return configuration_service.remove(_TYPE, name)


def test(name: str) -> str:
    databases = configuration_service.list(_TYPE, "name")
    db = next((d for d in databases if d["name"] == name), None)
    if db is None:
        raise KeyError(name)
    with connect(db):
        pass
    return name
