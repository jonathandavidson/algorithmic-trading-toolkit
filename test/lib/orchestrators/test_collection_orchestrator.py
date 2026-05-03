from unittest.mock import MagicMock

import pytest

from lib.adapters.database_adapter import DatabaseInsertError
from lib.orchestrators.collection_orchestrator import CollectionOrchestrator, DatasourceFetchError


def _make_orchestrator(
    rows: list | None = None,
) -> tuple[CollectionOrchestrator, MagicMock, MagicMock]:
    db_adapter = MagicMock()
    datasource_adapter = MagicMock()
    datasource_adapter.fetch_rows.return_value = rows if rows is not None else []
    return CollectionOrchestrator(db_adapter, datasource_adapter), db_adapter, datasource_adapter


# --- __init__ ---

def test_init_stores_db_adapter():
    db_adapter = MagicMock()
    datasource_adapter = MagicMock()
    orchestrator = CollectionOrchestrator(db_adapter, datasource_adapter)
    assert orchestrator._db_adapter is db_adapter


def test_init_stores_datasource_adapter():
    db_adapter = MagicMock()
    datasource_adapter = MagicMock()
    orchestrator = CollectionOrchestrator(db_adapter, datasource_adapter)
    assert orchestrator._datasource_adapter is datasource_adapter


# --- init_collection ---

def test_init_collection_calls_init_database():
    orchestrator, db_adapter, _ = _make_orchestrator()
    orchestrator.init_collection()
    db_adapter.init_database.assert_called_once()


def test_init_collection_returns_none():
    orchestrator, _, _ = _make_orchestrator()
    assert orchestrator.init_collection() is None


# --- run_collection ---

def test_run_collection_calls_fetch_rows():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    orchestrator.run_collection()
    datasource_adapter.fetch_rows.assert_called_once()


def test_run_collection_calls_insert_rows_with_fetched_rows():
    rows = [MagicMock(), MagicMock(), MagicMock()]
    orchestrator, db_adapter, _ = _make_orchestrator(rows=rows)
    orchestrator.run_collection()
    db_adapter.insert_rows.assert_called_once_with(rows)


def test_run_collection_returns_row_count():
    rows = [MagicMock(), MagicMock(), MagicMock()]
    orchestrator, _, _ = _make_orchestrator(rows=rows)
    assert orchestrator.run_collection() == 3


def test_run_collection_returns_zero_for_empty_rows():
    orchestrator, _, _ = _make_orchestrator(rows=[])
    assert orchestrator.run_collection() == 0


def test_run_collection_raises_datasource_fetch_error_on_fetch_failure():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_rows.side_effect = RuntimeError("network timeout")
    with pytest.raises(DatasourceFetchError):
        orchestrator.run_collection()


def test_run_collection_fetch_error_message_includes_original_error():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_rows.side_effect = RuntimeError("network timeout")
    with pytest.raises(DatasourceFetchError, match="network timeout"):
        orchestrator.run_collection()


def test_run_collection_fetch_error_chains_original_exception():
    orchestrator, _, datasource_adapter = _make_orchestrator()
    original = RuntimeError("network timeout")
    datasource_adapter.fetch_rows.side_effect = original
    with pytest.raises(DatasourceFetchError) as exc_info:
        orchestrator.run_collection()
    assert exc_info.value.__cause__ is original


def test_run_collection_does_not_call_insert_rows_when_fetch_fails():
    orchestrator, db_adapter, datasource_adapter = _make_orchestrator()
    datasource_adapter.fetch_rows.side_effect = RuntimeError("network timeout")
    with pytest.raises(DatasourceFetchError):
        orchestrator.run_collection()
    db_adapter.insert_rows.assert_not_called()


def test_run_collection_raises_database_insert_error_on_insert_failure():
    rows = [MagicMock()]
    orchestrator, db_adapter, _ = _make_orchestrator(rows=rows)
    db_adapter.insert_rows.side_effect = Exception("db connection lost")
    with pytest.raises(DatabaseInsertError):
        orchestrator.run_collection()


def test_run_collection_insert_error_chains_original_exception():
    rows = [MagicMock()]
    orchestrator, db_adapter, _ = _make_orchestrator(rows=rows)
    original = Exception("db connection lost")
    db_adapter.insert_rows.side_effect = original
    with pytest.raises(DatabaseInsertError) as exc_info:
        orchestrator.run_collection()
    assert exc_info.value.__cause__ is original
