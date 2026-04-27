from unittest.mock import MagicMock, patch

from lib.database import connect


def _db(db_type="postgresql"):
    return {
        "type": db_type,
        "username": "user",
        "password": "pass",
        "host": "localhost",
        "port": 5432,
        "dbname": "mydb",
    }


def test_connect_returns_connection():
    mock_engine = MagicMock()
    with patch("lib.database.sqlalchemy.create_engine", return_value=mock_engine):
        conn = connect(_db())
    mock_engine.connect.assert_called_once()
    assert conn == mock_engine.connect.return_value


def test_connect_postgres_alias():
    with patch("lib.database.sqlalchemy.create_engine", return_value=MagicMock()) as mock_create:
        connect(_db(db_type="postgres"))
    url = mock_create.call_args[0][0]
    assert url.drivername == "postgresql"


def test_connect_builds_url_from_db_config():
    with patch("lib.database.sqlalchemy.create_engine", return_value=MagicMock()) as mock_create:
        connect(_db())
    url = mock_create.call_args[0][0]
    assert url.username == "user"
    assert url.host == "localhost"
    assert url.port == 5432
    assert url.database == "mydb"
