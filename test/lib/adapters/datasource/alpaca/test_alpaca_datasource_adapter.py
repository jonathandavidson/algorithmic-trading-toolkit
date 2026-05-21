from unittest.mock import MagicMock, patch

import pytest

from lib.adapters.datasource.alpaca.alpaca_datasource_adapter import AlpacaDatasourceAdapter
from lib.models.alpaca.historical_bar import AlpacaHistoricalBar
from lib.services.configuration.datasource import DatasourceConfiguration
from lib.services.configuration.query import QueryConfiguration
from lib.services.configuration.type.query.historical_bars import HistoricalBarsQueryType


def _make_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(
        name="test-ds", type="alpaca", api_key="key123", api_secret="secret456",
    )
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


def _make_query_config(**overrides) -> QueryConfiguration:
    defaults = dict(
        name="bars-query",
        type="historical-bars",
        symbols=["BTC/USD"],
        frequency="1d",
        start="2026-05-01T00:00:00Z",
    )
    defaults.update(overrides)
    return QueryConfiguration(**defaults)


# --- get_model ---

def test_get_model_returns_alpaca_historical_bar_for_historical_bars():
    adapter = AlpacaDatasourceAdapter(_make_config())
    query_config = _make_query_config(type="historical-bars")
    assert adapter.get_model(query_config) is AlpacaHistoricalBar


def test_get_model_raises_for_unknown_query_type():
    adapter = AlpacaDatasourceAdapter(_make_config())
    query_config = _make_query_config(type="unknown-type")
    with pytest.raises(ValueError):
        adapter.get_model(query_config)


# --- run_query ---

def test_run_query_delegates_to_service_fetch_historical_bars():
    adapter = AlpacaDatasourceAdapter(_make_config())
    query_config = _make_query_config(type="historical-bars")
    with patch.object(adapter._service, 'fetch_historical_bars', return_value=iter([])) as mock_method:
        adapter.run_query(query_config)
    called_with = mock_method.call_args[0][0]
    assert isinstance(called_with, HistoricalBarsQueryType)


def test_run_query_returns_results_from_service():
    adapter = AlpacaDatasourceAdapter(_make_config())
    query_config = _make_query_config(type="historical-bars")
    page = [MagicMock(), MagicMock()]
    with patch.object(adapter._service, 'fetch_historical_bars', return_value=iter([page])):
        result = list(adapter.run_query(query_config))
    assert result == [page]


def test_run_query_raises_for_unknown_query_type():
    adapter = AlpacaDatasourceAdapter(_make_config())
    query_config = _make_query_config(type="unknown-type")
    with pytest.raises(ValueError):
        adapter.run_query(query_config)


# --- test_connection ---

def test_test_connection_delegates_to_service():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch.object(adapter._service, 'test_connection', return_value=True) as mock_method:
        result = adapter.test_connection()
    mock_method.assert_called_once()
    assert result is True


def test_test_connection_propagates_service_error():
    adapter = AlpacaDatasourceAdapter(_make_config())
    with patch.object(adapter._service, 'test_connection', side_effect=Exception("connection failed")):
        with pytest.raises(Exception, match="connection failed"):
            adapter.test_connection()
