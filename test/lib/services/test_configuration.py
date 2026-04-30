import pytest
import yaml

from lib.services.configuration import ConfigurationService


def _entry(name: str, **extra) -> dict:
    return {"name": name, **extra}


def _svc() -> ConfigurationService:
    return ConfigurationService()


def test_add_returns_configuration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = _entry("local", type="postgres")
    result = _svc().add("databases", "local", entry)
    assert result == entry


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _svc().add("databases", "local", _entry("local"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert config["databases"][0]["name"] == "local"


def test_add_raises_on_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "dup", _entry("dup"))
    with pytest.raises(ValueError, match="already exists"):
        svc.add("databases", "dup", _entry("dup"))


def test_add_types_are_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "shared-name", _entry("shared-name"))
    svc.add("collections", "shared-name", _entry("shared-name"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert len(config["collections"]) == 1


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert _svc().list("databases", "name") == []


def test_list_returns_all_entries(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "db1", _entry("db1"))
    svc.add("databases", "db2", _entry("db2"))

    results = svc.list("databases", "name")
    assert [e["name"] for e in results] == ["db1", "db2"]


def test_list_is_scoped_to_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "db1", _entry("db1"))
    svc.add("collections", "col1", _entry("col1"))

    assert len(svc.list("databases", "name")) == 1
    assert len(svc.list("collections", "name")) == 1


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "local", _entry("local"))
    assert svc.remove("databases", "local") == "local"


def test_remove_deletes_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "todelete", _entry("todelete"))
    svc.remove("databases", "todelete")

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert all(e["name"] != "todelete" for e in config.get("databases", []))


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        _svc().remove("databases", "ghost")


def test_remove_does_not_affect_other_types(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = _svc()
    svc.add("databases", "shared", _entry("shared"))
    svc.add("collections", "shared", _entry("shared"))
    svc.remove("databases", "shared")

    assert svc.list("databases", "name") == []
    assert len(svc.list("collections", "name")) == 1


def test_implements_interface(tmp_path, monkeypatch):
    from lib.services.interface.config_service import ConfigServiceInterface
    assert isinstance(ConfigurationService(), ConfigServiceInterface)
