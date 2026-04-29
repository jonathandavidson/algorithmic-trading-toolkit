import argparse

import yaml

from lib.commands.datasource import cmd_datasource_add


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

    config_file = tmp_path / ".config" / "hdc.config.yaml"
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

    config = yaml.safe_load((tmp_path / ".config" / "hdc.config.yaml").read_text())
    assert len(config["datasources"]) == 1
