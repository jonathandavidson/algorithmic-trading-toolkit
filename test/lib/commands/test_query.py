import argparse
from unittest.mock import MagicMock

import pytest
import yaml

from lib.commands.query import cmd_query, cmd_query_add, cmd_query_list, cmd_query_remove, cmd_query_update


def _make_args(**overrides) -> argparse.Namespace:
    defaults = dict(name="my-query")
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_query_add_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args())
    config_file = tmp_path / ".config" / "user.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["queries"]) == 1
    assert config["queries"][0]["name"] == "my-query"


def test_cmd_query_add_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args(name="my-query"))
    assert "my-query" in capsys.readouterr().out


def test_cmd_query_add_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args(name="dup"))
    capsys.readouterr()
    cmd_query_add(_make_args(name="dup"))
    assert "already exists" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["queries"]) == 1


def test_cmd_query_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_list(argparse.Namespace())
    assert "No queries configured" in capsys.readouterr().out


def test_cmd_query_list_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args(name="q1"))
    cmd_query_add(_make_args(name="q2"))
    capsys.readouterr()
    cmd_query_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "q1" in out
    assert "q2" in out


def test_cmd_query_remove_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_remove(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_query_remove_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_query_remove(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert all(q["name"] != "todelete" for q in config.get("queries", []))


def test_cmd_query_remove_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_add(_make_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_query_remove(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out
    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert any(q["name"] == "keep" for q in config["queries"])


def test_cmd_query_update_no_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_query_update(argparse.Namespace(name="my-query"))
    assert "No fields" in capsys.readouterr().out


def test_cmd_query_no_subcommand_prints_help():
    mock_parser = MagicMock()
    cmd_query(argparse.Namespace(query_command=None, query_parser=mock_parser))
    mock_parser.print_help.assert_called_once()
