import argparse
from unittest.mock import MagicMock, patch

import yaml

from lib.commands.collection import cmd_collection, cmd_collection_add, cmd_collection_init, cmd_collection_list, cmd_collection_remove, cmd_collection_run
from lib.commands.database import cmd_database_add
from lib.commands.datasource import cmd_datasource_add


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


def _make_datasource_args(**overrides) -> argparse.Namespace:
    defaults = dict(
        name="tesdc",
        datasource_type="alpaca",
        api_key="test_key",
        api_secret="test_secret",
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _make_collection_args(**overrides) -> argparse.Namespace:
    defaults = dict(
        name="bars",
        database="local",
        datasource="tesdc",
        type="historical-bars",
        frequency=None,
        start="2024-01-01T00:00:00",
        end=None,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_collection_add_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args())

    config_file = tmp_path / ".config" / "user.config.yaml"
    assert config_file.exists()
    config = yaml.safe_load(config_file.read_text())
    assert len(config["collections"]) == 1
    c = config["collections"][0]
    assert c["name"] == "bars"
    assert c["database"] == "local"
    assert c["type"] == "historical-bars"
    assert c["start"] == "2024-01-01T00:00:00+00:00"


def test_cmd_collection_add_optional_fields_absent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args())

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    c = config["collections"][0]
    assert "frequency" not in c
    assert "end" not in c


def test_cmd_collection_add_with_optional_fields(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(frequency="1m", end="2024-06-01T00:00:00"))

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    c = config["collections"][0]
    assert c["frequency"] == "1m"
    assert c["end"] == "2024-06-01T00:00:00+00:00"


def test_cmd_collection_add_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="c1"))
    cmd_collection_add(_make_collection_args(name="c2"))

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    names = [c["name"] for c in config["collections"]]
    assert names == ["c1", "c2"]


def test_cmd_collection_add_duplicate_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="dup"))
    capsys.readouterr()
    cmd_collection_add(_make_collection_args(name="dup"))
    out = capsys.readouterr().out
    assert "already exists" in out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["collections"]) == 1


def test_cmd_collection_add_prints_confirmation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="mybars"))
    assert "mybars" in capsys.readouterr().out


def test_cmd_collection_add_does_not_affect_databases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="local"))
    cmd_collection_add(_make_collection_args(database="local"))

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert len(config["databases"]) == 1
    assert len(config["collections"]) == 1


def test_cmd_collection_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_list(argparse.Namespace())
    assert "No collections configured" in capsys.readouterr().out


def test_cmd_collection_list_shows_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="c1"))
    cmd_collection_add(_make_collection_args(name="c2"))
    capsys.readouterr()

    cmd_collection_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "c1" in out
    assert "c2" in out


def test_cmd_collection_list_shows_all_required_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(
        name="bars", database="local", datasource="tesdc", type="historical-bars", start="2024-01-01T00:00:00"
    ))
    capsys.readouterr()

    cmd_collection_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "name=bars" in out
    assert "database=local" in out
    assert "datasource=tesdc" in out
    assert "type=historical-bars" in out
    assert "start=2024-01-01T00:00:00" in out


def test_cmd_collection_list_shows_optional_fields_when_present(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(frequency="1m", end="2024-06-01T00:00:00"))
    capsys.readouterr()

    cmd_collection_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "frequency=1m" in out
    assert "end=2024-06-01T00:00:00" in out


def test_cmd_collection_list_omits_optional_fields_when_absent(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args())
    capsys.readouterr()

    cmd_collection_list(argparse.Namespace())
    out = capsys.readouterr().out
    assert "frequency" not in out
    assert "end" not in out


def test_cmd_collection_remove_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_remove(argparse.Namespace(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_collection_remove_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="todelete"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_collection_remove(argparse.Namespace(name="todelete"))
    assert "removed" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert all(c["name"] != "todelete" for c in config.get("collections", []))


def test_cmd_collection_remove_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="keep"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_collection_remove(argparse.Namespace(name="keep"))
    assert "Cancelled" in capsys.readouterr().out

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    assert any(c["name"] == "keep" for c in config["collections"])


def test_cmd_collection_remove_does_not_affect_others(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="c1"))
    cmd_collection_add(_make_collection_args(name="c2"))
    monkeypatch.setattr("builtins.input", lambda _: "y")
    cmd_collection_remove(argparse.Namespace(name="c1"))

    config = yaml.safe_load((tmp_path / ".config" / "user.config.yaml").read_text())
    names = [c["name"] for c in config["collections"]]
    assert names == ["c2"]


def test_cmd_collection_init_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_init(argparse.Namespace(name="missing"))
    assert "missing" in capsys.readouterr().out


def test_cmd_collection_init_database_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="bars", database="missing"))
    capsys.readouterr()
    cmd_collection_init(argparse.Namespace(name="bars"))
    out = capsys.readouterr().out
    assert "not found" in out
    assert "missing" in out


def test_cmd_collection_init_cancelled(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="local"))
    cmd_collection_add(_make_collection_args(name="bars", database="local"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "n")
    cmd_collection_init(argparse.Namespace(name="bars"))
    assert "Cancelled" in capsys.readouterr().out


def test_cmd_collection_init_found_produces_no_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_database_add(_make_db_args(name="local"))
    cmd_datasource_add(_make_datasource_args(name="testdc"))
    cmd_collection_add(_make_collection_args(name="bars", database="local", datasource="testdc"))
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    with patch("lib.utils.database.create_engine", return_value=MagicMock()):
        with patch("lib.models.base.BaseModel.metadata"):
            cmd_collection_init(argparse.Namespace(name="bars"))
    assert "not found" not in capsys.readouterr().out


def test_cmd_collection_run_success(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="bars"))
    capsys.readouterr()
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        mock_runner_cls.return_value.run_collection.return_value = 10
        cmd_collection_run(argparse.Namespace(name="bars"))
    assert "10" in capsys.readouterr().out


def test_cmd_collection_run_collection_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_run(argparse.Namespace(name="missing"))
    out = capsys.readouterr().out
    assert "not found" in out
    assert "missing" in out


def test_cmd_collection_run_database_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="bars", database="missing-db"))
    capsys.readouterr()
    cmd_collection_run(argparse.Namespace(name="bars"))
    out = capsys.readouterr().out
    assert "not found" in out
    assert "missing-db" in out


def test_cmd_collection_run_generic_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd_collection_add(_make_collection_args(name="bars"))
    capsys.readouterr()
    with patch("lib.services.collection_runner.CollectionRunnerService") as mock_runner_cls:
        mock_runner_cls.return_value.run_collection.side_effect = RuntimeError("something broke")
        cmd_collection_run(argparse.Namespace(name="bars"))
    out = capsys.readouterr().out
    assert "Error" in out
    assert "something broke" in out


def test_cmd_collection_no_subcommand_prints_help():
    mock_parser = MagicMock()
    cmd_collection(argparse.Namespace(collection_command=None, collection_parser=mock_parser))
    mock_parser.print_help.assert_called_once()
