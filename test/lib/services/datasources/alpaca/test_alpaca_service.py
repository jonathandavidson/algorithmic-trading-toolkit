from unittest.mock import MagicMock, call, patch

import pytest
import requests

from lib.models.alpaca.historical_bar import AlpacaHistoricalBar
from lib.services.configuration.datasource import DatasourceConfiguration
from lib.services.datasources.alpaca.alpaca_service import AlpacaService


def _make_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(
        name="test-ds", type="alpaca", api_key="key123", api_secret="secret456",
    )
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


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


def _make_query_config_fields(**overrides) -> dict:
    defaults = dict(
        symbols=["BTC/USD"],
        frequency="1d",
        start="2026-05-01T00:00:00Z",
    )
    defaults.update(overrides)
    return defaults


# --- convert_to_model ---

def test_convert_to_model_returns_alpaca_historical_bar():
    service = AlpacaService(_make_config())
    result = service.convert_to_model(_make_bar_data())
    assert isinstance(result, AlpacaHistoricalBar)


def test_convert_to_model_maps_symbol():
    service = AlpacaService(_make_config())
    result = service.convert_to_model(_make_bar_data(symbol="ETH/USD"))
    assert result.symbol == "ETH/USD"


def test_convert_to_model_maps_time():
    service = AlpacaService(_make_config())
    result = service.convert_to_model(_make_bar_data(t="2026-01-01T00:00:00Z"))
    assert str(result.time) == "2026-01-01T00:00:00Z"


def test_convert_to_model_maps_ohlcv_fields():
    service = AlpacaService(_make_config())
    data = _make_bar_data(o=100, h=200, l=50, c=150, v=1.5)
    result = service.convert_to_model(data)
    assert result.open == 100
    assert result.high == 200
    assert result.low == 50
    assert result.close == 150
    assert result.volume == 1.5


def test_convert_to_model_maps_trade_count():
    service = AlpacaService(_make_config())
    result = service.convert_to_model(_make_bar_data(n=42))
    assert result.trade_count == 42


def test_convert_to_model_maps_volume_weighted_avg_price():
    service = AlpacaService(_make_config())
    result = service.convert_to_model(_make_bar_data(vw=12345))
    assert result.volume_weighted_avg_price == 12345


def test_convert_to_model_sets_source_from_config_type():
    service = AlpacaService(_make_config(type="alpaca"))
    result = service.convert_to_model(_make_bar_data())
    assert result.source == "alpaca"


# --- _fetch_with_retries ---

def test_fetch_with_retries_returns_json_on_success():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    mock_response.json.return_value = {"bars": {}}
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response):
        result = service._fetch_with_retries("https://example.com", {"symbols": "BTC/USD"})
    assert result == {"bars": {}}


def test_fetch_with_retries_does_not_retry_on_4xx():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    http_error = requests.exceptions.HTTPError(response=MagicMock(status_code=401))
    mock_response.raise_for_status.side_effect = http_error
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response) as mock_get:
        with pytest.raises(requests.exceptions.HTTPError):
            service._fetch_with_retries("https://example.com", {})
    assert mock_get.call_count == 1


def test_fetch_with_retries_retries_on_5xx_then_raises():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    http_error = requests.exceptions.HTTPError(response=MagicMock(status_code=503))
    mock_response.raise_for_status.side_effect = http_error
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response) as mock_get:
        with patch("lib.services.datasources.alpaca.alpaca_service.time.sleep"):
            with pytest.raises(requests.exceptions.HTTPError):
                service._fetch_with_retries("https://example.com", {})
    assert mock_get.call_count == 4  # 1 initial + 3 retries


def test_fetch_with_retries_retries_on_connection_error_then_raises():
    service = AlpacaService(_make_config())
    with patch(
        "lib.services.datasources.alpaca.alpaca_service.requests.get",
        side_effect=requests.exceptions.ConnectionError("unreachable"),
    ) as mock_get:
        with patch("lib.services.datasources.alpaca.alpaca_service.time.sleep"):
            with pytest.raises(requests.exceptions.ConnectionError):
                service._fetch_with_retries("https://example.com", {})
    assert mock_get.call_count == 4  # 1 initial + 3 retries


def test_fetch_with_retries_passes_url_to_request():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response) as mock_get:
        service._fetch_with_retries("https://custom.url/endpoint", {})
    assert mock_get.call_args[0][0] == "https://custom.url/endpoint"


def test_fetch_with_retries_uses_api_key_and_secret_as_auth():
    service = AlpacaService(_make_config(api_key="mykey", api_secret="mysecret"))
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response) as mock_get:
        service._fetch_with_retries("https://example.com", {})
    assert mock_get.call_args[1]["auth"] == ("mykey", "mysecret")


# --- fetch_historical_bars ---

def _make_api_response(symbols_bars: dict, next_page_token: str | None = None) -> dict:
    response: dict = {"bars": symbols_bars}
    if next_page_token is not None:
        response["next_page_token"] = next_page_token
    return response


def test_fetch_historical_bars_yields_single_page():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields())
    api_response = _make_api_response({"BTC/USD": [_make_bar_data()]})
    with patch.object(service, "_fetch_with_retries", return_value=api_response):
        pages = list(service.fetch_historical_bars(query_config))
    assert len(pages) == 1
    assert len(pages[0]) == 1
    assert isinstance(pages[0][0], AlpacaHistoricalBar)


def test_fetch_historical_bars_follows_pagination():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields())
    page1 = _make_api_response({"BTC/USD": [_make_bar_data()]}, next_page_token="token-abc")
    page2 = _make_api_response({"BTC/USD": [_make_bar_data()]})
    with patch.object(service, "_fetch_with_retries", side_effect=[page1, page2]):
        pages = list(service.fetch_historical_bars(query_config))
    assert len(pages) == 2


def test_fetch_historical_bars_passes_page_token_on_subsequent_requests():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields())
    page1 = _make_api_response({"BTC/USD": [_make_bar_data()]}, next_page_token="tok123")
    page2 = _make_api_response({"BTC/USD": []})
    with patch.object(service, "_fetch_with_retries", side_effect=[page1, page2]) as mock_fetch:
        list(service.fetch_historical_bars(query_config))
    second_call_params = mock_fetch.call_args_list[1][0][1]
    assert second_call_params.get("page_token") == "tok123"


def test_fetch_historical_bars_maps_1d_timeframe():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields(frequency="1d"))
    with patch.object(service, "_fetch_with_retries", return_value=_make_api_response({})) as mock_fetch:
        list(service.fetch_historical_bars(query_config))
    params = mock_fetch.call_args[0][1]
    assert params["timeframe"] == "1D"


def test_fetch_historical_bars_includes_end_when_set():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields(end="2026-05-31T00:00:00Z"))
    with patch.object(service, "_fetch_with_retries", return_value=_make_api_response({})) as mock_fetch:
        list(service.fetch_historical_bars(query_config))
    params = mock_fetch.call_args[0][1]
    assert "end" in params


def test_fetch_historical_bars_omits_end_when_not_set():
    service = AlpacaService(_make_config())
    from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType
    query_config = HistoricalBarsQueryType(**_make_query_config_fields())
    with patch.object(service, "_fetch_with_retries", return_value=_make_api_response({})) as mock_fetch:
        list(service.fetch_historical_bars(query_config))
    params = mock_fetch.call_args[0][1]
    assert "end" not in params


# --- test_connection ---

def test_test_connection_returns_true_on_success():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response):
        result = service.test_connection()
    assert result is True


def test_test_connection_calls_raise_for_status():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response):
        service.test_connection()
    mock_response.raise_for_status.assert_called_once()


def test_test_connection_uses_correct_url():
    service = AlpacaService(_make_config())
    mock_sys_config = MagicMock()
    mock_sys_config.test_url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
    with patch("lib.services.datasources.alpaca.alpaca_service.config", mock_sys_config):
        with patch("lib.services.datasources.alpaca.alpaca_service.requests.get") as mock_get:
            mock_get.return_value = MagicMock()
            service.test_connection()
    url = mock_get.call_args[0][0]
    assert url == "https://data.alpaca.markets/v1beta3/crypto/us/bars"


def test_test_connection_uses_api_key_and_secret_as_auth():
    service = AlpacaService(_make_config(api_key="mykey", api_secret="mysecret"))
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        service.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["auth"] == ("mykey", "mysecret")


def test_test_connection_sends_correct_headers():
    service = AlpacaService(_make_config())
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        service.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["headers"] == {"accept": "application/json"}


def test_test_connection_sends_correct_params():
    service = AlpacaService(_make_config())
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        service.test_connection()
    kwargs = mock_get.call_args[1]
    assert kwargs["params"] == {"symbols": "BTC/USD", "timeframe": "1D"}


def test_test_connection_propagates_http_error():
    service = AlpacaService(_make_config())
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
    with patch("lib.services.datasources.alpaca.alpaca_service.requests.get", return_value=mock_response):
        with pytest.raises(Exception, match="401 Unauthorized"):
            service.test_connection()
