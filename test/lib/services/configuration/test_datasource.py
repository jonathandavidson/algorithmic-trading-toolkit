import pytest
import requests
import yaml
from unittest.mock import MagicMock, patch

from lib.services.configuration.datasource import DatasourceConfiguration, DatasourceConfigurationService

datasource_service = DatasourceConfigurationService()


def _seed(**overrides) -> dict:
    defaults = dict(
        name="alpaca-prod",
        type="alpaca",
        api_key="key123",
        api_secret="secret456",
    )
    defaults.update(overrides)
    return datasource_service.add(DatasourceConfiguration(**defaults))


def test_add_returns_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    entry = datasource_service.add(DatasourceConfiguration(
        name="alpaca-prod", type="alpaca", api_key="key123", api_secret="secret456"
    ))
    assert entry.name == "alpaca-prod"
    assert entry.type == "alpaca"
    assert entry.api_key == "key123"
    assert entry.api_secret == "secret456"


def test_add_persists_to_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed()

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["datasources"]) == 1
    assert config["datasources"][0]["name"] == "alpaca-prod"


def test_add_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="ds1")
    _seed(name="ds2")

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
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

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["datasources"]) == 1


def test_list_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert datasource_service.list() == []


def test_list_returns_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="ds1")
    _seed(name="ds2")
    names = [ds.name for ds in datasource_service.list()]
    assert names == ["ds1", "ds2"]


def test_remove_returns_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed()
    assert datasource_service.remove("alpaca-prod") == "alpaca-prod"


def test_remove_deletes_from_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="todelete")
    datasource_service.remove("todelete")
    assert all(ds.name != "todelete" for ds in datasource_service.list())


def test_remove_raises_on_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        datasource_service.remove("ghost")


def test_test_returns_name_on_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="alpaca-prod")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    with patch("lib.services.configuration.datasource.requests.get", return_value=mock_response):
        assert datasource_service.test("alpaca-prod") == "alpaca-prod"


def test_test_raises_key_error_when_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(KeyError):
        datasource_service.test("missing")


def test_test_raises_on_http_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="alpaca-prod")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    with patch("lib.services.configuration.datasource.requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            datasource_service.test("alpaca-prod")


def test_test_sends_correct_request(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _seed(name="alpaca-prod", api_key="mykey", api_secret="mysecret")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    with patch("lib.services.configuration.datasource.requests.get", return_value=mock_response) as mock_post:
        datasource_service.test("alpaca-prod")
    mock_post.assert_called_once_with(
        "https://data.alpaca.markets/v1beta3/crypto/us/bars",
        auth=("mykey", "mysecret"),
        headers={"accept": "application/json"},
        params={"symbols": "BTC/USD", "timeframe": "1D"},
    )
