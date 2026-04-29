import argparse

import yaml

from lib.commands.add import cmd_add_database


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


def test_cmd_add_database_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args())

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


def test_cmd_add_database_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args(name="db1"))
    cmd_add_database(_make_db_args(name="db2"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    names = [db["name"] for db in config["databases"]]
    assert names == ["db1", "db2"]


def test_cmd_add_database_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args(name="myconn"))
    assert "myconn" in capsys.readouterr().out


def test_cmd_add_database_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args(name="dup"))
    capsys.readouterr()
    cmd_add_database(_make_db_args(name="dup"))
    out = capsys.readouterr().out
    assert "already exists" in out

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["databases"]) == 1


def test_cmd_add_database_first_is_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args(name="first"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert config["databases"][0].get("default") is True


def test_cmd_add_database_second_not_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_add_database(_make_db_args(name="first"))
    cmd_add_database(_make_db_args(name="second"))

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    dbs = {db["name"]: db for db in config["databases"]}
    assert dbs["first"].get("default") is True
    assert "default" not in dbs["second"]
