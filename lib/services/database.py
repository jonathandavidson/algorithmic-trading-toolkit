from lib.config import load_config, save_config
from lib.database import connect


def add(name: str, db_type: str, username: str, password: str, host: str, port: int, dbname: str) -> dict:
    config = load_config()
    databases = config.setdefault("databases", [])
    if any(db["name"] == name for db in databases):
        raise ValueError(f"Database '{name}' already exists.")
    is_first = len(databases) == 0
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
    databases.append(entry)
    save_config(config)
    return entry


def list() -> list[dict]:
    return load_config().get("databases", [])


def remove(name: str) -> str:
    config = load_config()
    databases = config.get("databases", [])
    if not any(db["name"] == name for db in databases):
        raise KeyError(name)
    config["databases"] = [db for db in databases if db["name"] != name]
    save_config(config)
    return name


def test(name: str) -> str:
    databases = load_config().get("databases", [])
    db = next((d for d in databases if d["name"] == name), None)
    if db is None:
        raise KeyError(name)
    with connect(db):
        pass
    return name
