from unittest.mock import MagicMock, patch

import pytest

from lib.adapters.database_adapter import DatabaseAdapter
from lib.services.configuration.database import DatabaseConfiguration


def _make_config(**overrides) -> DatabaseConfiguration:
    defaults = dict(
        name="local", type="postgres", username="user",
        password="pass", host="localhost", port=5432, dbname="mydb",
    )
    defaults.update(overrides)
    return DatabaseConfiguration(**defaults)


def test_init_database_drops_and_creates_tables():
    adapter = DatabaseAdapter(_make_config())
    mock_engine = MagicMock()
    with patch("lib.adapters.database_adapter.get_engine", return_value=mock_engine):
        with patch("lib.adapters.database_adapter.BaseModel.metadata") as mock_meta:
            adapter.init_database()
    mock_meta.drop_all.assert_called_once_with(mock_engine)
    mock_meta.create_all.assert_called_once_with(mock_engine)


def test_test_connection_executes_query_and_returns_true():
    adapter = DatabaseAdapter(_make_config())
    mock_engine = MagicMock()
    with patch("lib.adapters.database_adapter.get_engine", return_value=mock_engine):
        result = adapter.test_connection()
    assert result is True
    mock_engine.connect.assert_called_once()


def test_test_connection_passes_config_to_engine():
    config = _make_config(host="db.example.com", port=5433, dbname="prod")
    adapter = DatabaseAdapter(config)
    with patch("lib.adapters.database_adapter.get_engine", return_value=MagicMock()) as mock_get_engine:
        adapter.test_connection()
    call_arg = mock_get_engine.call_args[0][0]
    assert call_arg["host"] == "db.example.com"
    assert call_arg["port"] == 5433
    assert call_arg["dbname"] == "prod"


def test_insert_rows_adds_all_and_commits():
    adapter = DatabaseAdapter(_make_config())
    mock_session = MagicMock()
    bars = [MagicMock(), MagicMock()]
    with patch("lib.adapters.database_adapter.get_engine", return_value=MagicMock()):
        with patch("lib.adapters.database_adapter.Session") as mock_session_cls:
            mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)
            adapter.insert_rows(bars)
    mock_session.add_all.assert_called_once_with(bars)
    mock_session.commit.assert_called_once()


def test_insert_rows_with_empty_list():
    adapter = DatabaseAdapter(_make_config())
    mock_session = MagicMock()
    with patch("lib.adapters.database_adapter.get_engine", return_value=MagicMock()):
        with patch("lib.adapters.database_adapter.Session") as mock_session_cls:
            mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)
            adapter.insert_rows([])
    mock_session.add_all.assert_called_once_with([])
    mock_session.commit.assert_called_once()
