import argparse
from unittest.mock import MagicMock, patch

import requests
import yaml

from lib.commands.datasource import cmd_datasource, cmd_datasource_add, cmd_datasource_list, cmd_datasource_remove, cmd_datasource_test


def _make_args(**overrides) -> argparse.Namespace:
    defaults = dict(
        name="alpaca-prod",
        datasource_type="alpaca",
        api_key="key123",
        api_secret="secret456",
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_datasource_add_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args())

    config_file = tmp_path / ".config" / "user.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["datasources"]) == 1
    ds = config["datasources"][0]
    assert ds["name"] == "alpaca-prod"
    assert ds["type"] == "alpaca"
    assert ds["api_key"] == "key123"
    assert ds["api_secret"] == "secret456"


def test_cmd_datasource_add_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="my-source"))
    assert "my-source" in capsys.readouterr().out


def test_cmd_datasource_add_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="dup"))
    capsys.readouterr()
    cmd_datasource_add(_make_args(name="dup"))
    assert "already exists" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["datasources"]) == 1


def test_cmd_datasource_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_list(argparse.Namespace())
    assert "No datasources configured" in capsys.readouterr().out


def test_cmd_datasource_list_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="ds1"))
    cmd_datasource_add(_make_args(name="ds2"))
    capsys.readouterr()

    cmd_datasource_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "ds1" in out
    assert "ds2" in out


def test_cmd_datasource_list_masks_api_secret(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(api_secret="topsecret"))
    capsys.readouterr()

    cmd_datasource_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "topsecret" not in out
    assert "********" in out


def test_cmd_datasource_remove_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_remove(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_datasource_remove_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_datasource_remove(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert all(ds["name"] != "todelete" for ds in config.get("datasources", []))


def test_cmd_datasource_test_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_test(argparse.Namespace(name="missing"))
    assert "not found" in capsys.readouterr().out


def test_cmd_datasource_test_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="alpaca-prod"))
    capsys.readouterr()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    with patch("lib.services.configuration.datasource.requests.get", return_value=mock_response):
        cmd_datasource_test(argparse.Namespace(name="alpaca-prod"))
    assert "successful" in capsys.readouterr().out


def test_cmd_datasource_test_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="alpaca-prod"))
    capsys.readouterr()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    with patch("lib.services.configuration.datasource.requests.get", return_value=mock_response):
        cmd_datasource_test(argparse.Namespace(name="alpaca-prod"))
    out = capsys.readouterr().out
    assert "failed" in out
    assert "401 Unauthorized" in out


def test_cmd_datasource_remove_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_datasource_add(_make_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_datasource_remove(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert any(ds["name"] == "keep" for ds in config["datasources"])


def test_cmd_datasource_no_subcommand_prints_help():
    mock_parser = MagicMock()
    cmd_datasource(argparse.Namespace(datasource_command=None, datasource_parser=mock_parser))
    mock_parser.print_help.assert_called_once()
