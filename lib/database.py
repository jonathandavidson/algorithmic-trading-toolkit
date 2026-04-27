import sqlalchemy

_TYPE_ALIASES = {"postgres": "postgresql"}


def connect(db):
    dialect = _TYPE_ALIASES.get(db["type"], db["type"])
    url = sqlalchemy.URL.create(
        drivername=dialect,
        username=db["username"],
        password=db["password"],
        host=db["host"],
        port=db["port"],
        database=db["dbname"],
    )
    engine = sqlalchemy.create_engine(url)
    return engine.connect()
