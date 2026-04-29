import argparse
import os
from unittest.mock import MagicMock, patch

import pytest
import yaml

from lib.commands.configure import cmd_configure, cmd_configure_add_collection, cmd_configure_add_database, cmd_configure_init_collection, cmd_configure_list_collection, cmd_configure_list_database, cmd_configure_remove_collection, cmd_configure_remove_database, cmd_configure_test_database


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



def test_cmd_configure_test_database_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_test_database(argparse.Namespace(name="missing"))
    assert "not found" in capsys.readouterr().out


def test_cmd_configure_test_database_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb"))
    capsys.readouterr()

    with patch("lib.database.create_engine", return_value=MagicMock()):
        cmd_configure_test_database(argparse.Namespace(name="mydb"))

    assert "successful" in capsys.readouterr().out


def test_cmd_configure_test_database_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb"))
    capsys.readouterr()

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("connection refused")
    with patch("lib.database.create_engine", return_value=mock_engine):
        cmd_configure_test_database(argparse.Namespace(name="mydb"))

    out = capsys.readouterr().out
    assert "failed" in out
    assert "connection refused" in out


def _make_collection_args(**overrides):
    defaults = dict(
        name="bars",
        database="local",
        type="historical-bars",
        frequency=None,
        start="2024-01-01T00:00:00",
        end=None,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_configure_add_collection_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args())

    config_file = tmp_path / ".config" / "hdc.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["collections"]) == 1
    c = config["collections"][0]
    assert c["name"] == "bars"
    assert c["database"] == "local"
    assert c["type"] == "historical-bars"
    assert c["start"] == "2024-01-01T00:00:00"


def test_cmd_configure_add_collection_optional_fields_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args())

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    c = config["collections"][0]
    assert "frequency" not in c
    assert "end" not in c


def test_cmd_configure_add_collection_with_optional_fields(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(frequency="1m", end="2024-06-01T00:00:00"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    c = config["collections"][0]
    assert c["frequency"] == "1m"
    assert c["end"] == "2024-06-01T00:00:00"


def test_cmd_configure_add_collection_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="c1"))
    cmd_configure_add_collection(_make_collection_args(name="c2"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    names = [c["name"] for c in config["collections"]]
    assert names == ["c1", "c2"]


def test_cmd_configure_add_collection_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="dup"))
    capsys.readouterr()
    cmd_configure_add_collection(_make_collection_args(name="dup"))
    out = capsys.readouterr().out
    assert "already exists" in out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["collections"]) == 1


def test_cmd_configure_add_collection_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="mybars"))
    assert "mybars" in capsys.readouterr().out


def test_cmd_configure_add_collection_does_not_affect_databases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="local"))
    cmd_configure_add_collection(_make_collection_args(database="local"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert len(config["collections"]) == 1


def test_cmd_configure_init_collection_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_init_collection(argparse.Namespace(name="missing"))
    assert "missing" in capsys.readouterr().out


def test_cmd_configure_init_collection_found_produces_no_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="local"))
    cmd_configure_add_collection(_make_collection_args(name="bars", database="local"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    with patch("lib.database.create_engine", return_value=MagicMock()):
        with patch("lib.models.base.Base.metadata") as mock_meta:
            cmd_configure_init_collection(argparse.Namespace(name="bars"))
    assert "not found" not in capsys.readouterr().out


def test_cmd_configure_list_collection_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_list_collection(argparse.Namespace())
    assert "No collections configured" in capsys.readouterr().out


def test_cmd_configure_list_collection_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="c1"))
    cmd_configure_add_collection(_make_collection_args(name="c2"))
    capsys.readouterr()

    cmd_configure_list_collection(argparse.Namespace())
    out = capsys.readouterr().out
    assert "c1" in out
    assert "c2" in out


def test_cmd_configure_list_collection_shows_all_required_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(
        name="bars", database="local", type="historical-bars", start="2024-01-01T00:00:00"
    ))
    capsys.readouterr()

    cmd_configure_list_collection(argparse.Namespace())
    out = capsys.readouterr().out
    assert "name=bars" in out
    assert "database=local" in out
    assert "type=historical-bars" in out
    assert "start=2024-01-01T00:00:00" in out


def test_cmd_configure_list_collection_shows_optional_fields_when_present(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(frequency="1m", end="2024-06-01T00:00:00"))
    capsys.readouterr()

    cmd_configure_list_collection(argparse.Namespace())
    out = capsys.readouterr().out
    assert "frequency=1m" in out
    assert "end=2024-06-01T00:00:00" in out


def test_cmd_configure_list_collection_omits_optional_fields_when_absent(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args())
    capsys.readouterr()

    cmd_configure_list_collection(argparse.Namespace())
    out = capsys.readouterr().out
    assert "frequency" not in out
    assert "end" not in out


def test_cmd_configure_remove_collection_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_remove_collection(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_configure_remove_collection_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_configure_remove_collection(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert all(c["name"] != "todelete" for c in config.get("collections", []))


def test_cmd_configure_remove_collection_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_configure_remove_collection(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert any(c["name"] == "keep" for c in config["collections"])


def test_cmd_configure_remove_collection_does_not_affect_others(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_collection(_make_collection_args(name="c1"))
    cmd_configure_add_collection(_make_collection_args(name="c2"))
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_configure_remove_collection(argparse.Namespace(name="c1"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    names = [c["name"] for c in config["collections"]]
    assert names == ["c2"]


def test_cmd_configure_test_database_postgres_alias(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_configure_add_database(_make_db_args(name="mydb", db_type="postgres"))
    capsys.readouterr()

    with patch("lib.database.create_engine", return_value=MagicMock()) as mock_create:
        cmd_configure_test_database(argparse.Namespace(name="mydb"))

    url = mock_create.call_args[0][0]
    assert url.drivername == "postgresql"
