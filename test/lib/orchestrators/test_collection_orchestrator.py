from unittest.mock import MagicMock, call, patch

import pytest

from lib.adapters.database_adapter import DatabaseInsertError
from lib.orchestrators.collection_orchestrator import CollectionOrchestrator, DatasourceFetchError
from lib.services.configuration.collection import CollectionConfiguration, DatabaseNotFoundError, DatasourceNotFoundError


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


def _make_orchestrator(
    collection_config: CollectionConfiguration | None = None,
    db_config: MagicMock | None = None,
    datasource_config: MagicMock | None = None,
) -> tuple[CollectionOrchestrator, MagicMock, MagicMock]:
    if collection_config is None:
        collection_config = _make_collection_config()
    if db_config is None:
        db_config = MagicMock()
    if datasource_config is None:
        datasource_config = MagicMock()

    mock_db_adapter = MagicMock()
    mock_datasource_adapter = MagicMock()

    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService") as mock_ds_svc,
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance", return_value=mock_db_adapter),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter", return_value=mock_datasource_adapter),
    ):
        mock_db_svc.return_value.get_one.return_value = db_config
        mock_ds_svc.return_value.get_one.return_value = datasource_config
        orchestrator = CollectionOrchestrator(collection_config)

    return orchestrator, mock_db_adapter, mock_datasource_adapter


def test_init_fetches_database_config_by_name():
    config = _make_collection_config(database="prod-db")
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService") as mock_svc,
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter"),
    ):
        CollectionOrchestrator(config)
    mock_svc.return_value.get_one.assert_called_once_with("prod-db")


def test_init_fetches_datasource_config_by_name():
    config = _make_collection_config(datasource="my-alpaca")
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService") as mock_svc,
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter"),
    ):
        CollectionOrchestrator(config)
    mock_svc.return_value.get_one.assert_called_once_with("my-alpaca")


def test_init_creates_database_adapter_with_config():
    db_config = MagicMock()
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService") as mock_db_svc,
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance") as mock_get_instance,
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter"),
    ):
        mock_db_svc.return_value.get_one.return_value = db_config
        CollectionOrchestrator(_make_collection_config())
    mock_get_instance.assert_called_once_with(db_config)


def test_init_creates_datasource_adapter_with_config():
    ds_config = MagicMock()
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService") as mock_ds_svc,
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter") as mock_create,
    ):
        mock_ds_svc.return_value.get_one.return_value = ds_config
        CollectionOrchestrator(_make_collection_config())
    mock_create.assert_called_once_with(ds_config)


def test_init_raises_database_not_found_error():
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService") as mock_svc,
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter"),
    ):
        mock_svc.return_value.get_one.side_effect = KeyError("local")
        with pytest.raises(DatabaseNotFoundError):
            CollectionOrchestrator(_make_collection_config())


def test_init_raises_datasource_not_found_error():
    with (
        patch("lib.orchestrators.collection_orchestrator.DatabaseConfigurationService"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceConfigurationService") as mock_svc,
        patch("lib.orchestrators.collection_orchestrator.DatabaseAdapter.get_instance"),
        patch("lib.orchestrators.collection_orchestrator.DatasourceAdapterFactory.create_adapter"),
    ):
        mock_svc.return_value.get_one.side_effect = KeyError("alpaca")
        with pytest.raises(DatasourceNotFoundError):
            CollectionOrchestrator(_make_collection_config())


def test_init_collection_calls_init_database():
    orchestrator, mock_db_adapter, _ = _make_orchestrator()
    orchestrator.init_collection()
    mock_db_adapter.init_database.assert_called_once()


def test_run_collection_fetches_rows():
    collection_config = _make_collection_config()
    orchestrator, _, mock_ds_adapter = _make_orchestrator(collection_config=collection_config)
    orchestrator.run_collection()
    mock_ds_adapter.fetch_rows.assert_called_once_with(collection_config)


def test_run_collection_inserts_fetched_rows():
    orchestrator, mock_db_adapter, mock_ds_adapter = _make_orchestrator()
    rows = [MagicMock(), MagicMock()]
    mock_ds_adapter.fetch_rows.return_value = [rows]
    orchestrator.run_collection()
    mock_db_adapter.insert_rows.assert_called_once_with(rows)


def test_run_collection_inserts_each_page_separately():
    orchestrator, mock_db_adapter, mock_ds_adapter = _make_orchestrator()
    page1 = [MagicMock()]
    page2 = [MagicMock(), MagicMock()]
    mock_ds_adapter.fetch_rows.return_value = [page1, page2]
    orchestrator.run_collection()
    assert mock_db_adapter.insert_rows.call_count == 2
    mock_db_adapter.insert_rows.assert_any_call(page1)
    mock_db_adapter.insert_rows.assert_any_call(page2)


def test_run_collection_returns_row_count():
    orchestrator, _, mock_ds_adapter = _make_orchestrator()
    mock_ds_adapter.fetch_rows.return_value = [[MagicMock(), MagicMock(), MagicMock()]]
    result = orchestrator.run_collection()
    assert result == 3


def test_run_collection_returns_total_row_count_across_pages():
    orchestrator, _, mock_ds_adapter = _make_orchestrator()
    mock_ds_adapter.fetch_rows.return_value = [[MagicMock(), MagicMock()], [MagicMock()]]
    result = orchestrator.run_collection()
    assert result == 3


def test_run_collection_returns_zero_for_empty_fetch():
    orchestrator, _, mock_ds_adapter = _make_orchestrator()
    mock_ds_adapter.fetch_rows.return_value = []
    assert orchestrator.run_collection() == 0


def test_run_collection_raises_datasource_fetch_error():
    orchestrator, _, mock_ds_adapter = _make_orchestrator()
    mock_ds_adapter.fetch_rows.side_effect = RuntimeError("network error")
    with pytest.raises(DatasourceFetchError):
        orchestrator.run_collection()


def test_run_collection_raises_database_insert_error():
    orchestrator, mock_db_adapter, mock_ds_adapter = _make_orchestrator()
    mock_ds_adapter.fetch_rows.return_value = [[MagicMock()]]
    mock_db_adapter.insert_rows.side_effect = RuntimeError("db error")
    with pytest.raises(DatabaseInsertError):
        orchestrator.run_collection()
