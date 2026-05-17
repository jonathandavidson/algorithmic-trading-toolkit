from unittest.mock import MagicMock, patch

import pytest

from lib.adapters.factory.datasource_adapter_factory import DatasourceAdapterFactory, DatasourceNotFoundError
from lib.services.configuration.datasource import DatasourceConfiguration


def _make_config(**overrides) -> DatasourceConfiguration:
    defaults = dict(
        name="test-ds", type="alpaca", api_key="key123", api_secret="secret456",
    )
    defaults.update(overrides)
    return DatasourceConfiguration(**defaults)


def test_create_adapter_returns_alpaca_adapter_for_alpaca_type():
    from lib.adapters.datasource.alpaca.alpaca_datasource_adapter import AlpacaDatasourceAdapter

    config = _make_config(type="alpaca")
    adapter = DatasourceAdapterFactory.create_adapter(config)

    assert isinstance(adapter, AlpacaDatasourceAdapter)


def test_create_adapter_passes_config_to_alpaca_adapter():
    config = _make_config(type="alpaca", api_key="mykey", api_secret="mysecret")
    adapter = DatasourceAdapterFactory.create_adapter(config)

    assert adapter._config is config


def test_create_adapter_raises_for_unknown_type():
    config = _make_config(type="unknown_provider")

    with pytest.raises(DatasourceNotFoundError):
        DatasourceAdapterFactory.create_adapter(config)


def test_create_adapter_error_message_includes_datasource_type():
    config = _make_config(type="unknown_provider")

    with pytest.raises(DatasourceNotFoundError, match="unknown_provider"):
        DatasourceAdapterFactory.create_adapter(config)


def test_create_adapter_is_static_method():
    config = _make_config(type="alpaca")
    adapter = DatasourceAdapterFactory.create_adapter(config)

    assert adapter is not None


def test_create_adapter_lazy_imports_alpaca_module():
    config = _make_config(type="alpaca")

    with patch(
        "lib.adapters.datasource.alpaca.alpaca_datasource_adapter.AlpacaDatasourceAdapter"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        adapter = DatasourceAdapterFactory.create_adapter(config)

    mock_cls.assert_called_once_with(config)
    assert adapter is mock_instance
