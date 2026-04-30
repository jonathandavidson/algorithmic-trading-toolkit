import dataclasses

import pytest
import yaml
from dataclasses import dataclass

from lib.services.configuration import ConfigurationService
from lib.services.interface.config_service import ConfigServiceInterface
from lib.services.interface.configuration_type import ConfigurationTypeInterface


@dataclass
class _TestConfig(ConfigurationTypeInterface):
    name: str
    value: str = ""


def _entry(name: str, **extra) -> _TestConfig:
    return _TestConfig(name=name, **extra)


def test_add_returns_configuration_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = _entry("local", value="postgres")
    result = ConfigurationService("databases").add(entry)
    assert result == dataclasses.asdict(entry)


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ConfigurationService("databases").add(_entry("local"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert config["databases"][0]["name"] == "local"


def test_add_raises_on_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = ConfigurationService("databases")
    svc.add(_entry("dup"))
    with pytest.raises(ValueError, match="already exists"):
        svc.add(_entry("dup"))


def test_add_types_are_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ConfigurationService("databases").add(_entry("shared-name"))
    ConfigurationService("collections").add(_entry("shared-name"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert len(config["collections"]) == 1


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert ConfigurationService("databases").list("name") == []


def test_list_returns_all_entries(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = ConfigurationService("databases")
    svc.add(_entry("db1"))
    svc.add(_entry("db2"))

    results = svc.list("name")
    assert [e["name"] for e in results] == ["db1", "db2"]


def test_list_is_scoped_to_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ConfigurationService("databases").add(_entry("db1"))
    ConfigurationService("collections").add(_entry("col1"))

    assert len(ConfigurationService("databases").list("name")) == 1
    assert len(ConfigurationService("collections").list("name")) == 1


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = ConfigurationService("databases")
    svc.add(_entry("local"))
    assert svc.remove("local") == "local"


def test_remove_deletes_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = ConfigurationService("databases")
    svc.add(_entry("todelete"))
    svc.remove("todelete")

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert all(e["name"] != "todelete" for e in config.get("databases", []))


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        ConfigurationService("databases").remove("ghost")


def test_remove_does_not_affect_other_types(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ConfigurationService("databases").add(_entry("shared"))
    ConfigurationService("collections").add(_entry("shared"))
    ConfigurationService("databases").remove("shared")

    assert ConfigurationService("databases").list("name") == []
    assert len(ConfigurationService("collections").list("name")) == 1


def test_get_one_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    svc = ConfigurationService("databases")
    svc.add(_entry("local", value="postgres"))
    result = svc.get_one("local")
    assert result["name"] == "local"
    assert result["value"] == "postgres"


def test_get_one_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        ConfigurationService("databases").get_one("ghost")


def test_get_one_is_scoped_to_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ConfigurationService("databases").add(_entry("local"))
    with pytest.raises(KeyError):
        ConfigurationService("collections").get_one("local")


def test_implements_interface(tmp_path, monkeypatch):
    assert isinstance(ConfigurationService("databases"), ConfigServiceInterface)
