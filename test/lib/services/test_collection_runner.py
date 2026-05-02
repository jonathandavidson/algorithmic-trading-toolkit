from unittest.mock import MagicMock, patch

import pytest

from lib.services.collection_runner import CollectionRunnerService
from lib.services.configuration.collection import CollectionConfiguration, DatabaseNotFoundError, DatasourceNotFoundError
from lib.services.configuration.database import DatabaseConfiguration
from lib.services.configuration.datasource import DatasourceConfiguration


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


def _make_database_config(**overrides) -> DatabaseConfiguration:
    defaults = dict(
        name="local", type="postgres", username="user",
        password="pass", host="localhost", port=5432, dbname="mydb",
    )
    defaults.update(overrides)
    return DatabaseConfiguration(**defaults)


def _make_datasource_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(name="alpaca", type="alpaca", api_key="key", api_secret="secret")
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


def _make_runner(
    collection_config: CollectionConfiguration | None = None,
) -> tuple[CollectionRunnerService, MagicMock]:
    if collection_config is None:
        collection_config = _make_collection_config()
    mock_orchestrator = MagicMock()
    with (
        patch("lib.services.collection_runner.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.services.collection_runner.DatasourceConfigurationService") as mock_ds_svc,
        patch.object(CollectionRunnerService, "_build_collection_orchestrator", return_value=mock_orchestrator),
    ):
        mock_db_svc.return_value.get_one.return_value = _make_database_config()
        mock_ds_svc.return_value.get_one.return_value = _make_datasource_config()
        runner = CollectionRunnerService(collection_config)
    return runner, mock_orchestrator


def test_init_raises_database_not_found():
    config = _make_collection_config(database="missing")
    with patch("lib.services.collection_runner.DatabaseConfigurationService") as mock_db_svc:
        mock_db_svc.return_value.get_one.side_effect = KeyError("missing")
        with pytest.raises(DatabaseNotFoundError, match="missing"):
            CollectionRunnerService(config)


def test_init_raises_datasource_not_found():
    config = _make_collection_config(datasource="missing")
    with (
        patch("lib.services.collection_runner.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.services.collection_runner.DatasourceConfigurationService") as mock_ds_svc,
    ):
        mock_db_svc.return_value.get_one.return_value = _make_database_config()
        mock_ds_svc.return_value.get_one.side_effect = KeyError("missing")
        with pytest.raises(DatasourceNotFoundError, match="missing"):
            CollectionRunnerService(config)


def test_init_looks_up_database_by_collection_database_field():
    config = _make_collection_config(database="mydb")
    with (
        patch("lib.services.collection_runner.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.services.collection_runner.DatasourceConfigurationService") as mock_ds_svc,
        patch.object(CollectionRunnerService, "_build_collection_orchestrator", return_value=MagicMock()),
    ):
        mock_db_svc.return_value.get_one.return_value = _make_database_config()
        mock_ds_svc.return_value.get_one.return_value = _make_datasource_config()
        CollectionRunnerService(config)
    mock_db_svc.return_value.get_one.assert_called_once_with("mydb")


def test_init_looks_up_datasource_by_collection_datasource_field():
    config = _make_collection_config(datasource="myds")
    with (
        patch("lib.services.collection_runner.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.services.collection_runner.DatasourceConfigurationService") as mock_ds_svc,
        patch.object(CollectionRunnerService, "_build_collection_orchestrator", return_value=MagicMock()),
    ):
        mock_db_svc.return_value.get_one.return_value = _make_database_config()
        mock_ds_svc.return_value.get_one.return_value = _make_datasource_config()
        CollectionRunnerService(config)
    mock_ds_svc.return_value.get_one.assert_called_once_with("myds")


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
