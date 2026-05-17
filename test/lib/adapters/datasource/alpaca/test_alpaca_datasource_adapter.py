from unittest.mock import MagicMock, call, patch

import pytest
import requests

from lib.adapters.datasource.alpaca.alpaca_datasource_adapter import AlpacaDatasourceAdapter
from lib.models.historical_bars import HistoricalBar
from lib.services.configuration.collection import CollectionConfiguration
from lib.services.configuration.datasource import DatasourceConfiguration


def _make_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(
        name="test-ds", type="alpaca", api_key="key123", api_secret="secret456",
    )
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


def _make_collection_config(**overrides) -> CollectionConfiguration:
    defaults = dict(
        name="bars",
        database="local",
        datasource="alpaca",
        type="historical-bars",
        start="2026-05-01T00:00:00Z",
        end="2026-05-05T00:00:00Z",
        frequency="1d",
        symbols=["BTC/USD"],
    )
    defaults.update(overrides)
    return CollectionConfiguration(**defaults)


def _make_bar_data(**overrides) -> dict:
    defaults = dict(
        symbol="BTC/USD",
        t="2026-05-27T10:18:00Z",
        o=28999,
        h=29003,
        l=28999,
        c=29003,
        v=0.01,
        n=4,
        vw=29001,
    )
    defaults.update(overrides)
    return defaults


# --- convert_to_model ---

def test_convert_to_model_returns_historical_bar():
    adapter = AlpacaDatasourceAdapter(_make_config())
    result = adapter.convert_to_model(_make_bar_data())
    assert isinstance(result, HistoricalBar)


def test_convert_to_model_maps_symbol():
    adapter = AlpacaDatasourceAdapter(_make_config())
    result = adapter.convert_to_model(_make_bar_data(symbol="ETH/USD"))
    assert result.symbol == "ETH/USD"


def test_convert_to_model_maps_time():
    adapter = AlpacaDatasourceAdapter(_make_config())
    result = adapter.convert_to_model(_make_bar_data(t="2026-01-01T00:00:00Z"))
    assert str(result.time) == "2026-01-01T00:00:00Z"


def test_convert_to_model_maps_ohlcv_fields():
    adapter = AlpacaDatasourceAdapter(_make_config())
    data = _make_bar_data(o=100, h=200, l=50, c=150, v=1.5)
    result = adapter.convert_to_model(data)
    assert result.open == 100
    assert result.high == 200
    assert result.low == 50
    assert result.close == 150
    assert result.volume == 1.5


def test_convert_to_model_maps_trade_count():
    adapter = AlpacaDatasourceAdapter(_make_config())
    result = adapter.convert_to_model(_make_bar_data(n=42))
    assert result.trade_count == 42


def test_convert_to_model_maps_volume_weighted_avg_price():
    adapter = AlpacaDatasourceAdapter(_make_config())
    result = adapter.convert_to_model(_make_bar_data(vw=12345))
    assert result.volume_weighted_avg_price == 12345


def test_convert_to_model_sets_source_from_config_type():
    adapter = AlpacaDatasourceAdapter(_make_config(type="alpaca"))
    result = adapter.convert_to_model(_make_bar_data())
    assert result.source == "alpaca"


# --- fetch_rows ---

_MOCK_RESPONSE_JSON = {
    "bars": {
        "BTC/USD": [
            {"t": "2026-05-27T10:18:00Z", "o": 28999, "h": 29003, "l": 28999, "c": 29003, "v": 0.01, "n": 4, "vw": 29001},
            {"t": "2022-05-27T10:18:00Z", "o": 28999, "h": 29003, "l": 28999, "c": 29003, "v": 0.01, "n": 4, "vw": 29001},
        ]
    },
    "next_page_token": None,
}


def _make_fetch_mock() -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = _MOCK_RESPONSE_JSON
    return mock_response


def _make_page_response(bars_by_symbol: dict, next_page_token: str | None = None) -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = {"bars": bars_by_symbol, "next_page_token": next_page_token}
    return mock_response


_BAR_ENTRY = {"t": "2026-05-27T10:18:00Z", "o": 28999, "h": 29003, "l": 28999, "c": 29003, "v": 0.01, "n": 4, "vw": 29001}


def test_fetch_rows_yields_list():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        result = next(adapter.fetch_rows(_make_collection_config()))
    assert isinstance(result, list)


def test_fetch_rows_yields_historical_bar_instances():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        result = next(adapter.fetch_rows(_make_collection_config()))
    assert all(isinstance(bar, HistoricalBar) for bar in result)


def test_fetch_rows_yields_two_bars_from_mock_data():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        result = next(adapter.fetch_rows(_make_collection_config()))
    assert len(result) == 2


def test_fetch_rows_assigns_symbol_from_response_key():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        result = next(adapter.fetch_rows(_make_collection_config()))
    assert all(bar.symbol == "BTC/USD" for bar in result)


def test_fetch_rows_maps_field_values_correctly():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        bar = next(adapter.fetch_rows(_make_collection_config()))[0]
    assert bar.open == 28999
    assert bar.high == 29003
    assert bar.low == 28999
    assert bar.close == 29003
    assert bar.volume == 0.01
    assert bar.trade_count == 4
    assert bar.volume_weighted_avg_price == 29001


def test_fetch_rows_calls_raise_for_status():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_response = _make_fetch_mock()
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=mock_response):
        next(adapter.fetch_rows(_make_collection_config()))
    mock_response.raise_for_status.assert_called_once()


def test_fetch_rows_uses_correct_url():
    adapter = AlpacaDatasourceAdapter(_make_config(type="alpaca"))
    mock_sys_config = MagicMock()
    mock_sys_config.fetch_url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.config", mock_sys_config):
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
            mock_get.return_value = _make_fetch_mock()
            next(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_args[0][0] == "https://data.alpaca.markets/v1beta3/crypto/us/bars"


def test_fetch_rows_uses_api_key_and_secret_as_auth():
    adapter = AlpacaDatasourceAdapter(_make_config(api_key="mykey", api_secret="mysecret"))
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_args[1]["auth"] == ("mykey", "mysecret")


def test_fetch_rows_propagates_http_error():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=mock_response):
        with pytest.raises(Exception, match="403 Forbidden"):
            next(adapter.fetch_rows(_make_collection_config()))


def test_fetch_rows_sends_symbols_from_collection_config():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(symbols=["BTC/USD", "ETH/USD"])
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert mock_get.call_args[1]["params"]["symbols"] == "BTC/USD,ETH/USD"


def test_fetch_rows_omits_symbols_when_none():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(symbols=None)
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert "symbols" not in mock_get.call_args[1]["params"]


def test_fetch_rows_converts_1d_frequency_to_alpaca_timeframe():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(frequency="1d")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert mock_get.call_args[1]["params"]["timeframe"] == "1D"


def test_fetch_rows_converts_1m_frequency_to_alpaca_timeframe():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(frequency="1m")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert mock_get.call_args[1]["params"]["timeframe"] == "1M"


def test_fetch_rows_sends_start_from_collection_config():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(start="2025-01-15T00:00:00Z")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert mock_get.call_args[1]["params"]["start"] == "2025-01-15T00:00:00+00:00"


def test_fetch_rows_sends_end_from_collection_config():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(end="2025-01-20T00:00:00Z")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert mock_get.call_args[1]["params"]["end"] == "2025-01-20T00:00:00+00:00"


def test_fetch_rows_sends_page_limit_from_config():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_sys_config = MagicMock()
    mock_sys_config.page_limit = 500
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.config", mock_sys_config):
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
            mock_get.return_value = _make_fetch_mock()
            next(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_args[1]["params"]["limit"] == 500


def test_fetch_rows_omits_end_when_none():
    adapter = AlpacaDatasourceAdapter(_make_config())
    collection_config = _make_collection_config(end=None)
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(collection_config))
    assert "end" not in mock_get.call_args[1]["params"]


# --- fetch_rows pagination ---

def test_fetch_rows_yields_one_page_when_next_page_token_is_none():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        pages = list(adapter.fetch_rows(_make_collection_config()))
    assert len(pages) == 1


def test_fetch_rows_yields_multiple_pages_when_next_page_token_present():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.side_effect = [
            _make_page_response({"BTC/USD": [_BAR_ENTRY]}, next_page_token="token123"),
            _make_page_response({"BTC/USD": [_BAR_ENTRY]}, next_page_token=None),
        ]
        pages = list(adapter.fetch_rows(_make_collection_config()))
    assert len(pages) == 2


def test_fetch_rows_sends_next_page_token_as_page_token_param():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.side_effect = [
            _make_page_response({"BTC/USD": [_BAR_ENTRY]}, next_page_token="token123"),
            _make_page_response({"BTC/USD": [_BAR_ENTRY]}, next_page_token=None),
        ]
        list(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_args_list[1][1]["params"]["page_token"] == "token123"


def test_fetch_rows_does_not_send_page_token_on_first_request():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = _make_fetch_mock()
        next(adapter.fetch_rows(_make_collection_config()))
    assert "page_token" not in mock_get.call_args_list[0][1]["params"]


# --- fetch_rows retries ---

def _make_http_error(status_code: int) -> requests.exceptions.HTTPError:
    mock_response = MagicMock()
    mock_response.status_code = status_code
    return requests.exceptions.HTTPError(response=mock_response)


def test_fetch_rows_retries_on_500_and_succeeds():
    adapter = AlpacaDatasourceAdapter(_make_config())
    success_mock = _make_fetch_mock()
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            mock_get.side_effect = [_make_http_error(500), success_mock]
            result = next(adapter.fetch_rows(_make_collection_config()))
    assert len(result) == 2


def test_fetch_rows_retries_on_connection_error_and_succeeds():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            mock_get.side_effect = [requests.exceptions.ConnectionError(), _make_fetch_mock()]
            result = next(adapter.fetch_rows(_make_collection_config()))
    assert isinstance(result, list)


def test_fetch_rows_retries_on_timeout_and_succeeds():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            mock_get.side_effect = [requests.exceptions.Timeout(), _make_fetch_mock()]
            result = next(adapter.fetch_rows(_make_collection_config()))
    assert isinstance(result, list)


def test_fetch_rows_does_not_retry_on_4xx_error():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            mock_get.side_effect = _make_http_error(403)
            with pytest.raises(requests.exceptions.HTTPError):
                next(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_count == 1


def test_fetch_rows_raises_after_max_retries_exhausted():
    adapter = AlpacaDatasourceAdapter(_make_config())
    error = requests.exceptions.ConnectionError("network down")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", side_effect=error):
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            with pytest.raises(requests.exceptions.ConnectionError):
                next(adapter.fetch_rows(_make_collection_config()))


def test_fetch_rows_attempts_four_times_before_giving_up():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep"):
            mock_get.side_effect = requests.exceptions.Timeout()
            with pytest.raises(requests.exceptions.Timeout):
                next(adapter.fetch_rows(_make_collection_config()))
    assert mock_get.call_count == 4


def test_fetch_rows_uses_exponential_backoff_delays():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep") as mock_sleep:
            mock_get.side_effect = requests.exceptions.Timeout()
            with pytest.raises(requests.exceptions.Timeout):
                next(adapter.fetch_rows(_make_collection_config()))
    assert mock_sleep.call_args_list == [call(1.0), call(2.0), call(4.0)]


def test_fetch_rows_succeeds_on_first_attempt_without_sleeping():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=_make_fetch_mock()):
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.time.sleep") as mock_sleep:
            next(adapter.fetch_rows(_make_collection_config()))
    mock_sleep.assert_not_called()


# --- test_connection ---

def test_test_connection_returns_true_on_success():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_response = MagicMock()
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=mock_response):
        result = adapter.test_connection()
    assert result is True


def test_test_connection_calls_raise_for_status():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_response = MagicMock()
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=mock_response):
        adapter.test_connection()
    mock_response.raise_for_status.assert_called_once()


def test_test_connection_uses_correct_url():
    adapter = AlpacaDatasourceAdapter(_make_config(type="alpaca"))
    mock_sys_config = MagicMock()
    mock_sys_config.test_url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.config", mock_sys_config):
        with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
            mock_get.return_value = MagicMock()
            adapter.test_connection()
    url = mock_get.call_args[0][0]
    assert url == "https://data.alpaca.markets/v1beta3/crypto/us/bars"


def test_test_connection_uses_api_key_and_secret_as_auth():
    adapter = AlpacaDatasourceAdapter(_make_config(api_key="mykey", api_secret="mysecret"))
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        adapter.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["auth"] == ("mykey", "mysecret")


def test_test_connection_sends_correct_headers():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        adapter.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["headers"] == {"accept": "application/json"}


def test_test_connection_sends_correct_params():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        adapter.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["params"] == {"symbols": "BTC/USD", "timeframe": "1D"}


def test_test_connection_propagates_http_error():
    adapter = AlpacaDatasourceAdapter(_make_config())
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
    with patch("lib.adapters.datasource.alpaca.alpaca_datasource_adapter.requests.get", return_value=mock_response):
        with pytest.raises(Exception, match="401 Unauthorized"):
            adapter.test_connection()
