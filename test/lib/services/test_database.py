import pytest
import yaml
from unittest.mock import MagicMock, patch

import lib.services.database as database_service


def _seed_db(tmp_path, **overrides) -> None:
    defaults = dict(
        name="local",
        db_type="postgres",
        username="user",
        password="pass",
        host="localhost",
        port=5432,
        dbname="mydb",
    )
    defaults.update(overrides)
    database_service.add(**defaults)


def test_add_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = database_service.add("local", "postgres", "user", "pass", "localhost", 5432, "mydb")
    assert entry["name"] == "local"
    assert entry["type"] == "postgres"
    assert entry["host"] == "localhost"
    assert entry["port"] == 5432
    assert entry["dbname"] == "mydb"


def test_add_first_entry_is_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = database_service.add("first", "postgres", "user", "pass", "localhost", 5432, "mydb")
    assert entry.get("default") is True


def test_add_second_entry_not_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    database_service.add("first", "postgres", "user", "pass", "localhost", 5432, "mydb")
    entry = database_service.add("second", "postgres", "user", "pass", "localhost", 5432, "mydb")
    assert "default" not in entry


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    database_service.add("local", "postgres", "user", "pass", "localhost", 5432, "mydb")

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert config["databases"][0]["name"] == "local"


def test_add_raises_on_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    database_service.add("dup", "postgres", "user", "pass", "localhost", 5432, "mydb")
    with pytest.raises(ValueError, match="already exists"):
        database_service.add("dup", "postgres", "user", "pass", "localhost", 5432, "mydb")


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert database_service.list() == []


def test_list_returns_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path, name="db1")
    _seed_db(tmp_path, name="db2")
    names = [db["name"] for db in database_service.list()]
    assert names == ["db1", "db2"]


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path)
    result = database_service.remove("local")
    assert result == "local"


def test_remove_deletes_from_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path, name="todelete")
    database_service.remove("todelete")
    assert all(db["name"] != "todelete" for db in database_service.list())


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        database_service.remove("ghost")


def test_test_returns_name_on_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path, name="mydb")
    with patch("lib.database.create_engine", return_value=MagicMock()):
        result = database_service.test("mydb")
    assert result == "mydb"


def test_test_raises_key_error_when_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        database_service.test("missing")


def test_test_raises_on_connection_failure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path, name="mydb")
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("connection refused")
    with patch("lib.database.create_engine", return_value=mock_engine):
        with pytest.raises(Exception, match="connection refused"):
            database_service.test("mydb")


def test_test_postgres_alias(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_db(tmp_path, name="mydb", db_type="postgres")
    with patch("lib.database.create_engine", return_value=MagicMock()) as mock_create:
        database_service.test("mydb")
    url = mock_create.call_args[0][0]
    assert url.drivername == "postgresql"
