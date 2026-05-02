from unittest.mock import MagicMock, patch

import pytest
import requests

from lib.adapters.datasource_adapter import DatasourceAdapter, _TEST_URLS
from lib.models.historical_bars import HistoricalBar
from lib.services.configuration.datasource import DatasourceConfiguration


def _make_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(name="alpaca", type="alpaca", api_key="key", api_secret="secret")
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


def test_convert_to_model_maps_fields():
    adapter = DatasourceAdapter(_make_config())
    data = {
        'symbol': 'BTC/USD',
        't': '2024-01-01T00:00:00Z',
        'o': 100.0,
        'h': 110.0,
        'l': 90.0,
        'c': 105.0,
        'v': 1.5,
    }
    bar = adapter._convert_to_model(data)
    assert isinstance(bar, HistoricalBar)
    assert bar.symbol == 'BTC/USD'
    assert bar.open == 100.0
    assert bar.high == 110.0
    assert bar.low == 90.0
    assert bar.close == 105.0
    assert bar.volume == 1.5


def test_fetch_historical_bars_returns_all_bars():
    adapter = DatasourceAdapter(_make_config())
    bars = adapter.fetch_historical_bars()
    assert len(bars) == 2


def test_fetch_historical_bars_returns_historical_bar_instances():
    adapter = DatasourceAdapter(_make_config())
    bars = adapter.fetch_historical_bars()
    assert all(isinstance(b, HistoricalBar) for b in bars)


def test_fetch_historical_bars_sets_symbol():
    adapter = DatasourceAdapter(_make_config())
    bars = adapter.fetch_historical_bars()
    assert all(b.symbol == 'BTC/USD' for b in bars)


def test_test_connection_calls_correct_url():
    config = _make_config(type="alpaca", api_key="mykey", api_secret="mysecret")
    adapter = DatasourceAdapter(config)
    mock_response = MagicMock()
    with patch("lib.adapters.datasource_adapter.requests.get", return_value=mock_response) as mock_get:
        result = adapter.test_connection()
    assert result is True
    mock_get.assert_called_once()
    url = mock_get.call_args[0][0]
    assert url == _TEST_URLS["alpaca"]


def test_test_connection_sends_credentials():
    config = _make_config(type="alpaca", api_key="mykey", api_secret="mysecret")
    adapter = DatasourceAdapter(config)
    with patch("lib.adapters.datasource_adapter.requests.get", return_value=MagicMock()) as mock_get:
        adapter.test_connection()
    assert mock_get.call_args[1]["auth"] == ("mykey", "mysecret")


def test_test_connection_raises_on_http_error():
    adapter = DatasourceAdapter(_make_config())
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError()
    with patch("lib.adapters.datasource_adapter.requests.get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            adapter.test_connection()
