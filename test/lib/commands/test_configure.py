import argparse
import os
from unittest.mock import MagicMock, patch

import pytest
import yaml

from lib.commands.configure import cmd_configure, cmd_configure_add_database, cmd_configure_list_database, cmd_configure_remove_database, cmd_configure_test_database


def test_cmd_configure_no_subcommand_prints_help(capsys):
    parser = argparse.ArgumentParser()
    args = parser.parse_args([])
    args.configure_command = None
    args.configure_parser = parser
    cmd_configure(args)
    assert capsys.readouterr().out != ""


def _make_db_args(**overrides):
    defaults = dict(
        name="local",
        db_type="postgres",
        username="user",
        password="pass",
        host="localhost",
        port=5432,
        dbname="mydb",
        set_default=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_configure_add_database_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args())

    config_file = tmp_path / ".config" / "hdc.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["databases"]) == 1
    db = config["databases"][0]
    assert db["name"] == "local"
    assert db["type"] == "postgres"
    assert db["host"] == "localhost"
    assert db["port"] == 5432
    assert db["dbname"] == "mydb"


def test_cmd_configure_add_database_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="db1"))
    cmd_configure_add_database(_make_db_args(name="db2"))

    config_file = tmp_path / ".config" / "hdc.config.yaml"
    config = yaml.safe_load(config_file.read_text())
    names = [db["name"] for db in config["databases"]]
    assert names == ["db1", "db2"]


def test_cmd_configure_add_database_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="myconn"))
    assert "myconn" in capsys.readouterr().out


def test_cmd_configure_list_database_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_list_database(argparse.Namespace())
    assert "No databases configured" in capsys.readouterr().out


def test_cmd_configure_list_database_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="prod", password="secret"))
    cmd_configure_add_database(_make_db_args(name="staging", password="s3cr3t"))
    capsys.readouterr()

    cmd_configure_list_database(argparse.Namespace())
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_configure_list_database_shows_default(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="primary"))
    cmd_configure_add_database(_make_db_args(name="secondary"))
    capsys.readouterr()

    cmd_configure_list_database(argparse.Namespace())
    lines = capsys.readouterr().out.splitlines()
    primary_line = next(l for l in lines if "primary" in l)
    secondary_line = next(l for l in lines if "secondary" in l)
    assert "default=true" in primary_line
    assert "default=true" not in secondary_line


def test_cmd_configure_list_database_masks_password(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="db", password="supersecret"))
    capsys.readouterr()

    cmd_configure_list_database(argparse.Namespace())
    out = capsys.readouterr().out
    assert "supersecret" not in out
    assert "********" in out


def test_cmd_configure_add_database_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="dup"))
    capsys.readouterr()
    cmd_configure_add_database(_make_db_args(name="dup"))
    out = capsys.readouterr().out
    assert "already exists" in out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1


def test_cmd_configure_remove_database_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_remove_database(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_configure_remove_database_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_configure_remove_database(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert all(db["name"] != "todelete" for db in config.get("databases", []))


def test_cmd_configure_remove_database_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_configure_remove_database(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert any(db["name"] == "keep" for db in config["databases"])


def test_cmd_configure_add_database_first_is_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="first"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    db = config["databases"][0]
    assert db.get("default") is True


def test_cmd_configure_add_database_second_without_flag_not_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="first"))
    cmd_configure_add_database(_make_db_args(name="second"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    dbs = {db["name"]: db for db in config["databases"]}
    assert dbs["first"].get("default") is True
    assert "default" not in dbs["second"]


def test_cmd_configure_add_database_with_default_flag_transfers_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="first"))
    cmd_configure_add_database(_make_db_args(name="second", set_default=True))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    dbs = {db["name"]: db for db in config["databases"]}
    assert "default" not in dbs["first"]
    assert dbs["second"].get("default") is True


def test_cmd_configure_test_database_no_default(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_test_database(argparse.Namespace())
    assert "No default database found" in capsys.readouterr().out


def test_cmd_configure_test_database_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb"))
    capsys.readouterr()

    with patch("lib.database.sqlalchemy.create_engine", return_value=MagicMock()):
        cmd_configure_test_database(argparse.Namespace())

    assert "successful" in capsys.readouterr().out


def test_cmd_configure_test_database_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb"))
    capsys.readouterr()

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("connection refused")
    with patch("lib.database.sqlalchemy.create_engine", return_value=mock_engine):
        cmd_configure_test_database(argparse.Namespace())

    out = capsys.readouterr().out
    assert "failed" in out
    assert "connection refused" in out


def test_cmd_configure_test_database_postgres_alias(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb", db_type="postgres"))
    capsys.readouterr()

    with patch("lib.database.sqlalchemy.create_engine", return_value=MagicMock()) as mock_create:
        cmd_configure_test_database(argparse.Namespace())

    url = mock_create.call_args[0][0]
    assert url.drivername == "postgresql"
