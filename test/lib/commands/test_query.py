import argparse
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from lib.commands.query import cmd_query, cmd_query_add, cmd_query_list, cmd_query_remove, cmd_query_update

_SYSTEM_CONFIG = {"query_types": [{"name": "historical-bars"}]}


def _write_system_config(tmp_path: Path) -> None:
    config_dir = tmp_path / ".config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "system.config.yaml").write_text(yaml.dump(_SYSTEM_CONFIG))


def _make_args(**overrides) -> argparse.Namespace:
    defaults = dict(
        name="my-query",
        type="historical-bars",
        symbols=["BTC/USD"],
        frequency="1d",
        start=None,
        end=None,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_query_add_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args())
    config_file = tmp_path / ".config" / "user.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["queries"]) == 1
    q = config["queries"][0]
    assert q["name"] == "my-query"
    assert q["type"] == "historical-bars"
    assert q["symbols"] == ["BTC/USD"]
    assert q["frequency"] == "1d"


def test_cmd_query_add_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="my-query"))
    assert "my-query" in capsys.readouterr().out


def test_cmd_query_add_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="dup"))
    capsys.readouterr()
    cmd_query_add(_make_args(name="dup"))
    assert "already exists" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["queries"]) == 1


def test_cmd_query_add_unknown_type(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(type="no-such-type"))
    assert "Unknown query type" in capsys.readouterr().out


def test_cmd_query_add_missing_required_field(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(symbols=None))
    assert "Invalid query configuration" in capsys.readouterr().out


def test_cmd_query_add_invalid_frequency(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(frequency="5m"))
    assert "Invalid query configuration" in capsys.readouterr().out


def test_cmd_query_add_with_optional_dates(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(start="2024-01-01T00:00:00", end="2024-06-01T00:00:00"))
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    q = config["queries"][0]
    assert "start" in q
    assert "end" in q


def test_cmd_query_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_list(argparse.Namespace())
    assert "No queries configured" in capsys.readouterr().out


def test_cmd_query_list_shows_all_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="q1"))
    cmd_query_add(_make_args(name="q2"))
    capsys.readouterr()
    cmd_query_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "q1" in out
    assert "q2" in out
    assert "historical-bars" in out
    assert "BTC/USD" in out


def test_cmd_query_remove_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_remove(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_query_remove_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_query_remove(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert all(q["name"] != "todelete" for q in config.get("queries", []))


def test_cmd_query_remove_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_query_remove(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert any(q["name"] == "keep" for q in config["queries"])


def test_cmd_query_update_no_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_update(argparse.Namespace(name="my-query", symbols=None, frequency=None, start=None, end=None))
    assert "No fields" in capsys.readouterr().out


def test_cmd_query_update_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_update(argparse.Namespace(name="ghost", symbols=["ETH/USD"], frequency=None, start=None, end=None))
    assert "not found" in capsys.readouterr().out


def test_cmd_query_update_applies_change(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="my-query"))
    capsys.readouterr()
    cmd_query_update(argparse.Namespace(name="my-query", symbols=["ETH/USD"], frequency=None, start=None, end=None))
    assert "updated" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert config["queries"][0]["symbols"] == ["ETH/USD"]


def test_cmd_query_update_type_is_immutable(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_system_config(tmp_path)
    cmd_query_add(_make_args(name="my-query"))
    capsys.readouterr()
    cmd_query_update(argparse.Namespace(name="my-query", symbols=["ETH/USD"], frequency=None, start=None, end=None))
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert config["queries"][0]["type"] == "historical-bars"


def test_cmd_query_no_subcommand_prints_help():
    mock_parser = MagicMock()
    cmd_query(argparse.Namespace(query_command=None, query_parser=mock_parser))
    mock_parser.print_help.assert_called_once()
