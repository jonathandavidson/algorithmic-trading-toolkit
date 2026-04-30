import pytest
import yaml
from unittest.mock import MagicMock, patch

import lib.services.collection as collection_service
import lib.services.database as database_service
from lib.services.collection import CollectionConfiguration, CollectionNotFoundError, DatabaseNotFoundError
from lib.services.database import DatabaseConfiguration


def _seed_collection(**overrides) -> dict:
    defaults = dict(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
    )
    defaults.update(overrides)
    return collection_service.add(CollectionConfiguration(**defaults))


def _seed_database(**overrides) -> dict:
    defaults = dict(
        name="local",
        type="postgres",
        username="user",
        password="pass",
        host="localhost",
        port=5432,
        dbname="mydb",
    )
    defaults.update(overrides)
    return database_service.add(DatabaseConfiguration(**defaults))


def test_add_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = collection_service.add(CollectionConfiguration(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
    ))
    assert entry.name == "bars"
    assert entry.database == "local"
    assert entry.type == "historical-bars"
    assert entry.start == "2024-01-01T00:00:00"


def test_add_omits_optional_fields_when_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = collection_service.add(CollectionConfiguration(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
    ))
    assert entry.frequency is None
    assert entry.end is None


def test_add_includes_optional_fields_when_provided(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = collection_service.add(CollectionConfiguration(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
        frequency="1m",
        end="2024-06-01T00:00:00",
    ))
    assert entry.frequency == "1m"
    assert entry.end == "2024-06-01T00:00:00"


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection()

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["collections"]) == 1
    assert config["collections"][0]["name"] == "bars"


def test_add_raises_on_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="dup")
    with pytest.raises(ValueError, match="already exists"):
        _seed_collection(name="dup")


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert collection_service.list() == []


def test_list_returns_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="c1")
    _seed_collection(name="c2")
    names = [c.name for c in collection_service.list()]
    assert names == ["c1", "c2"]


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection()
    assert collection_service.remove("bars") == "bars"


def test_remove_deletes_from_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="todelete")
    collection_service.remove("todelete")
    assert all(c["name"] != "todelete" for c in collection_service.list())


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.remove("ghost")


def test_init_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_database(name="local")
    _seed_collection(name="bars", database="local")
    with patch("lib.utils.database.create_engine", return_value=MagicMock()):
        with patch("lib.models.base.Base.metadata"):
            assert collection_service.init("bars") == "bars"


def test_init_raises_when_collection_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.init("missing")


def test_init_raises_when_database_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="missing-db")
    with pytest.raises(DatabaseNotFoundError, match="missing-db"):
        collection_service.init("bars")


def test_init_drops_and_creates_tables(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_database(name="local")
    _seed_collection(name="bars", database="local")
    with patch("lib.utils.database.create_engine", return_value=MagicMock()):
        with patch("lib.models.base.Base.metadata") as mock_meta:
            collection_service.init("bars")
    assert mock_meta.drop_all.called
    assert mock_meta.create_all.called


def test_run_raises_when_collection_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.run("missing")


def test_run_raises_when_database_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="missing-db")
    with pytest.raises(DatabaseNotFoundError, match="missing-db"):
        collection_service.run("bars")


def test_run_returns_inserted_count(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_database(name="local")
    _seed_collection(name="bars", database="local")
    with patch("lib.utils.database.create_engine", return_value=MagicMock()):
        with patch("lib.services.collection.Session") as mock_session_cls:
            mock_session_cls.return_value.__enter__.return_value = MagicMock()
            count = collection_service.run("bars")
    assert count == 3
