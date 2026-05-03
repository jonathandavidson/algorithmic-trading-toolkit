from unittest.mock import MagicMock

import pytest

from lib.adapters.database_adapter import DatabaseInsertError
from lib.adapters.datasource_adapter import DatasourceFetchError
from lib.orchestrators.collection_orchestrator import CollectionOrchestrator


def _make_orchestrator() -> tuple[CollectionOrchestrator, MagicMock, MagicMock]:
    db_adapter = MagicMock()
    datasource_adapter = MagicMock()
    return CollectionOrchestrator(db_adapter, datasource_adapter), db_adapter, datasource_adapter


def test_init_collection_calls_init_database():
    orchestrator, db_adapter, _ = _make_orchestrator()
    orchestrator.init_collection()
    db_adapter.init_database.assert_called_once()


def test_run_collection_fetches_bars_from_datasource():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.return_value = []
    orchestrator.run_collection()
    datasource_adapter.fetch_historical_bars.assert_called_once()


def test_run_collection_inserts_fetched_bars():
    orchestrator, db_adapter, datasource_adapter = _make_orchestrator()
    bars = [MagicMock(), MagicMock(), MagicMock()]
    datasource_adapter.fetch_historical_bars.return_value = bars
    orchestrator.run_collection()
    db_adapter.insert_historical_bars.assert_called_once_with(bars)


def test_run_collection_returns_bar_count():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    bars = [MagicMock(), MagicMock()]
    datasource_adapter.fetch_historical_bars.return_value = bars
    result = orchestrator.run_collection()
    assert result == 2


def test_run_collection_returns_zero_for_empty_result():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.return_value = []
    result = orchestrator.run_collection()
    assert result == 0


def test_run_collection_wraps_fetch_failure_as_datasource_fetch_error():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.side_effect = RuntimeError("network down")
    with pytest.raises(DatasourceFetchError):
        orchestrator.run_collection()


def test_run_collection_fetch_error_preserves_original_message():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.side_effect = RuntimeError("timeout")
    with pytest.raises(DatasourceFetchError, match="timeout"):
        orchestrator.run_collection()


def test_run_collection_wraps_insert_failure_as_database_insert_error():
    orchestrator, db_adapter, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.return_value = [MagicMock()]
    db_adapter.insert_historical_bars.side_effect = RuntimeError("constraint violation")
    with pytest.raises(DatabaseInsertError):
        orchestrator.run_collection()


def test_run_collection_insert_error_preserves_original_message():
    orchestrator, db_adapter, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_historical_bars.return_value = [MagicMock()]
    db_adapter.insert_historical_bars.side_effect = RuntimeError("unique constraint")
    with pytest.raises(DatabaseInsertError, match="unique constraint"):
        orchestrator.run_collection()
