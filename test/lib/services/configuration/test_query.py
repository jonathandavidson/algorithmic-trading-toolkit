import pytest
import yaml

from lib.services.configuration.query import QueryConfiguration, QueryConfigurationService, QueryNotFoundError

query_service = QueryConfigurationService()


def _seed(**overrides) -> QueryConfiguration:
    defaults = dict(name="my-query")
    defaults.update(overrides)
    return query_service.add(QueryConfiguration(**defaults))


def test_add_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = query_service.add(QueryConfiguration(name="my-query"))
    assert entry.name == "my-query"


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed()
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["queries"]) == 1
    assert config["queries"][0]["name"] == "my-query"


def test_add_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="q1")
    _seed(name="q2")
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    names = [q["name"] for q in config["queries"]]
    assert names == ["q1", "q2"]


def test_add_raises_on_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="dup")
    with pytest.raises(ValueError, match="already exists"):
        _seed(name="dup")


def test_add_duplicate_does_not_write(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="dup")
    try:
        _seed(name="dup")
    except ValueError:
        pass
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["queries"]) == 1


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert query_service.list() == []


def test_list_returns_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="q1")
    _seed(name="q2")
    names = [q.name for q in query_service.list()]
    assert names == ["q1", "q2"]


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed()
    assert query_service.remove("my-query") == "my-query"


def test_remove_deletes_from_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="todelete")
    query_service.remove("todelete")
    assert all(q.name != "todelete" for q in query_service.list())


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(QueryNotFoundError):
        query_service.remove("ghost")


def test_get_one_returns_query(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="my-query")
    result = query_service.get_one("my-query")
    assert result.name == "my-query"


def test_get_one_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        query_service.get_one("ghost")


def test_update_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(QueryNotFoundError):
        query_service.update("ghost", {})
