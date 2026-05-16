from datetime import datetime, timezone

import pytest
import yaml
from unittest.mock import MagicMock, patch

from lib.services.configuration.collection import CollectionConfiguration, CollectionConfigurationService, CollectionNotFoundError, DatabaseNotFoundError, DatasourceNotFoundError, QueryNotFoundError
from lib.services.configuration.database import DatabaseConfiguration, DatabaseConfigurationService
from lib.services.configuration.query import QueryConfiguration, QueryConfigurationService

collection_service = CollectionConfigurationService()
database_service = DatabaseConfigurationService()


@pytest.fixture(autouse=True)
def hdc_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HDC_SECRET", "test-secret-value")


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
    assert entry.start == datetime(2024, 1, 1, tzinfo=timezone.utc)


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
    assert entry.symbols is None


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
    assert entry.end == datetime(2024, 6, 1, tzinfo=timezone.utc)


def test_add_includes_symbols_when_provided(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = collection_service.add(CollectionConfiguration(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
        symbols=["AAPL", "MSFT"],
    ))
    assert entry.symbols == ["AAPL", "MSFT"]


def test_add_omits_symbols_from_config_when_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection()
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert "symbols" not in config["collections"][0]


def test_add_persists_symbols_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(symbols=["AAPL", "MSFT"])
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert config["collections"][0]["symbols"] == ["AAPL", "MSFT"]


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection()

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
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
    _seed_collection(name="bars", database="local")
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        assert collection_service.init("bars") == "bars"
    mock_runner_cls.return_value.init_collection.assert_called_once()


def test_init_raises_when_collection_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.init("missing")


def test_init_raises_when_database_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="missing-db")
    with pytest.raises(DatabaseNotFoundError, match="missing-db"):
        collection_service.init("bars")


def test_init_raises_when_datasource_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_database(name="local")
    _seed_collection(name="bars", database="local", datasource="missing-ds")
    with pytest.raises(DatasourceNotFoundError, match="missing-ds"):
        collection_service.init("bars")


def test_init_delegates_to_runner(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="local")
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        collection_service.init("bars")
    mock_runner_cls.return_value.init_collection.assert_called_once()


def test_run_raises_when_collection_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.run("missing")


def test_run_raises_when_database_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="missing-db")
    with pytest.raises(DatabaseNotFoundError, match="missing-db"):
        collection_service.run("bars")


def test_run_raises_when_datasource_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_database(name="local")
    _seed_collection(name="bars", database="local", datasource="missing-ds")
    with pytest.raises(DatasourceNotFoundError, match="missing-ds"):
        collection_service.run("bars")


def test_run_returns_inserted_count(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="local")
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        mock_runner_cls.return_value.run_collection.return_value = 5
        count = collection_service.run("bars")
    assert count == 5


def test_run_delegates_to_runner(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="local")
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        mock_runner_cls.return_value.run_collection.return_value = 0
        collection_service.run("bars")
    mock_runner_cls.return_value.run_collection.assert_called_once()


def test_get_one_returns_collection(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars")
    result = collection_service.get_one("bars")
    assert result.name == "bars"


def test_update_changes_field(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="old-db")
    collection_service.update("bars", {"database": "new-db"})
    entry = collection_service.get_one("bars")
    assert entry.database == "new-db"


def test_update_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars", database="old-db")
    collection_service.update("bars", {"database": "new-db"})

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert config["collections"][0]["database"] == "new-db"


def test_update_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CollectionNotFoundError):
        collection_service.update("ghost", {"database": "x"})


def _seed_query(name: str = "my-query") -> None:
    QueryConfigurationService().add(QueryConfiguration(name=name, type="historical-bars", symbols=["AAPL"], frequency="1d"))


def test_add_raises_query_not_found_when_invalid_query(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(QueryNotFoundError):
        collection_service.add(CollectionConfiguration(
            name="bars",
            database="local",
            type="historical-bars",
            start="2024-01-01T00:00:00",
            query="missing-query",
        ))


def test_add_succeeds_when_query_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_query("my-query")
    entry = collection_service.add(CollectionConfiguration(
        name="bars",
        database="local",
        type="historical-bars",
        start="2024-01-01T00:00:00",
        query="my-query",
    ))
    assert entry.query == "my-query"


def test_add_persists_query_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_query("my-query")
    _seed_collection(name="bars", query="my-query")
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert config["collections"][0]["query"] == "my-query"


def test_add_omits_query_from_config_when_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection()
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert "query" not in config["collections"][0]


def test_update_raises_query_not_found_when_invalid_query(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_collection(name="bars")
    with pytest.raises(QueryNotFoundError):
        collection_service.update("bars", {"query": "missing-query"})


def test_update_succeeds_when_query_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed_query("my-query")
    _seed_collection(name="bars")
    collection_service.update("bars", {"query": "my-query"})
    entry = collection_service.get_one("bars")
    assert entry.query == "my-query"
