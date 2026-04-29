import pytest
import yaml

import lib.services.datasource as datasource_service


def _seed(**overrides) -> dict:
    defaults = dict(
        name="alpaca-prod",
        datasource_type="alpaca",
        api_key="key123",
        api_secret="secret456",
    )
    defaults.update(overrides)
    return datasource_service.add(**defaults)


def test_add_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = datasource_service.add("alpaca-prod", "alpaca", "key123", "secret456")
    assert entry["name"] == "alpaca-prod"
    assert entry["type"] == "alpaca"
    assert entry["api_key"] == "key123"
    assert entry["api_secret"] == "secret456"


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed()

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["datasources"]) == 1
    assert config["datasources"][0]["name"] == "alpaca-prod"


def test_add_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="ds1")
    _seed(name="ds2")

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    names = [ds["name"] for ds in config["datasources"]]
    assert names == ["ds1", "ds2"]


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

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["datasources"]) == 1
