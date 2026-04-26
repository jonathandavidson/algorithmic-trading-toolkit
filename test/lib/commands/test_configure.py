import argparse
import os

import pytest
import yaml

from lib.commands.configure import cmd_configure, cmd_configure_add_database, cmd_configure_list_database


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
