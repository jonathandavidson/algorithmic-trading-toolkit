import argparse
from unittest.mock import MagicMock, patch

import yaml

from lib.commands.database import cmd_database_add, cmd_database_list, cmd_database_remove, cmd_database_test


def _make_db_args(**overrides) -> argparse.Namespace:
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


def test_cmd_database_add_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args())

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


def test_cmd_database_add_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="db1"))
    cmd_database_add(_make_db_args(name="db2"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    names = [db["name"] for db in config["databases"]]
    assert names == ["db1", "db2"]


def test_cmd_database_add_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="myconn"))
    assert "myconn" in capsys.readouterr().out


def test_cmd_database_add_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="dup"))
    capsys.readouterr()
    cmd_database_add(_make_db_args(name="dup"))
    out = capsys.readouterr().out
    assert "already exists" in out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1


def test_cmd_database_add_first_is_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="first"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert config["databases"][0].get("default") is True


def test_cmd_database_add_second_not_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="first"))
    cmd_database_add(_make_db_args(name="second"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    dbs = {db["name"]: db for db in config["databases"]}
    assert dbs["first"].get("default") is True
    assert "default" not in dbs["second"]


def test_cmd_database_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_list(argparse.Namespace())
    assert "No databases configured" in capsys.readouterr().out


def test_cmd_database_list_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="prod", password="secret"))
    cmd_database_add(_make_db_args(name="staging", password="s3cr3t"))
    capsys.readouterr()

    cmd_database_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_database_list_shows_default(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="primary"))
    cmd_database_add(_make_db_args(name="secondary"))
    capsys.readouterr()

    cmd_database_list(argparse.Namespace())
    lines = capsys.readouterr().out.splitlines()
    primary_line = next(l for l in lines if "primary" in l)
    secondary_line = next(l for l in lines if "secondary" in l)
    assert "default=true" in primary_line
    assert "default=true" not in secondary_line


def test_cmd_database_list_masks_password(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="db", password="supersecret"))
    capsys.readouterr()

    cmd_database_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "supersecret" not in out
    assert "********" in out


def test_cmd_database_remove_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_remove(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_database_remove_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_database_remove(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert all(db["name"] != "todelete" for db in config.get("databases", []))


def test_cmd_database_remove_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_database_remove(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert any(db["name"] == "keep" for db in config["databases"])


def test_cmd_database_test_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_test(argparse.Namespace(name="missing"))
    assert "not found" in capsys.readouterr().out


def test_cmd_database_test_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="mydb"))
    capsys.readouterr()

    with patch("lib.database.create_engine", return_value=MagicMock()):
        cmd_database_test(argparse.Namespace(name="mydb"))

    assert "successful" in capsys.readouterr().out


def test_cmd_database_test_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="mydb"))
    capsys.readouterr()

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("connection refused")
    with patch("lib.database.create_engine", return_value=mock_engine):
        cmd_database_test(argparse.Namespace(name="mydb"))

    out = capsys.readouterr().out
    assert "failed" in out
    assert "connection refused" in out


def test_cmd_database_test_postgres_alias(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="mydb", db_type="postgres"))
    capsys.readouterr()

    with patch("lib.database.create_engine", return_value=MagicMock()) as mock_create:
        cmd_database_test(argparse.Namespace(name="mydb"))

    url = mock_create.call_args[0][0]
    assert url.drivername == "postgresql"
