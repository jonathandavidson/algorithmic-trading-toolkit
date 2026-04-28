from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Connection, Engine

_TYPE_ALIASES = {"postgres": "postgresql"}


def get_engine(db: dict) -> Engine:
    dialect = _TYPE_ALIASES.get(db["type"], db["type"])
    url = URL.create(
        drivername=dialect,
        username=db["username"],
        password=db["password"],
        host=db["host"],
        port=db["port"],
        database=db["dbname"],
    )
    return create_engine(url)


def connect(db: dict) -> Connection:
    return get_engine(db).connect()
