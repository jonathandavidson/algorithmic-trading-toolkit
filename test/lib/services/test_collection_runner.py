from unittest.mock import MagicMock, patch

import pytest

from lib.services.collection_runner import CollectionRunnerService
from lib.services.configuration.collection import CollectionConfiguration


def _make_collection_config(**overrides) -> CollectionConfiguration:
    defaults = dict(
        name="bars",
        database="local",
        datasource="alpaca",
        type="historical-bars",
        start="2024-01-01T00:00:00",
    )
    defaults.update(overrides)
    return CollectionConfiguration(**defaults)


def _make_runner(
    collection_config: CollectionConfiguration | None = None,
) -> tuple[CollectionRunnerService, MagicMock]:
    if collection_config is None:
        collection_config = _make_collection_config()
    mock_orchestrator = MagicMock()
    with (
        patch.object(CollectionRunnerService, "_build_collection_orchestrator", return_value=mock_orchestrator),
    ):
        runner = CollectionRunnerService(collection_config)
    return runner, mock_orchestrator


def test_init_collection_delegates_to_orchestrator():
    runner, mock_orchestrator = _make_runner()
    runner.init_collection()
    mock_orchestrator.init_collection.assert_called_once()


def test_init_collection_returns_collection_name():
    runner, _ = _make_runner(_make_collection_config(name="my-bars"))
    assert runner.init_collection() == "my-bars"


def test_run_collection_delegates_to_orchestrator():
    runner, mock_orchestrator = _make_runner()
    runner.run_collection()
    mock_orchestrator.run_collection.assert_called_once()


def test_test_connections_calls_datasource_adapter():
    runner, mock_orchestrator = _make_runner()
    runner.test_connections()
    mock_orchestrator._datasource_adapter.test_connection.assert_called_once()


def test_test_connections_calls_db_adapter():
    runner, mock_orchestrator = _make_runner()
    runner.test_connections()
    mock_orchestrator._db_adapter.test_connection.assert_called_once()


def test_test_connections_returns_collection_name():
    runner, _ = _make_runner(_make_collection_config(name="my-bars"))
    assert runner.test_connections() == "my-bars"
