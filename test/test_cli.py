import pytest
import yaml
from unittest.mock import patch

import cli


def test_build_parser_has_run_subcommand():
    parser = cli.build_parser()
    args = parser.parse_args(["run", "collection", "--name", "my-collection"])
    assert args.command == "run"
    assert args.name == "my-collection"


def test_build_parser_version_flag():
    parser = cli.build_parser()
    args = parser.parse_args(["--version"])
    assert args.show_version is True


def test_main_version_flag(capsys):
    with patch("sys.argv", ["hdc", "--version"]):
        cli.main()
    assert capsys.readouterr().out.strip() == "historical-data-collector 0.1.0"


def test_main_run_collection_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with patch("sys.argv", ["hdc", "run", "collection", "--name", "missing"]):
        cli.main()
    assert "not found" in capsys.readouterr().out


def test_main_no_args_exits(capsys):
    with patch("sys.argv", ["hdc"]):
        with pytest.raises(SystemExit) as exc:
            cli.main()
    assert exc.value.code == 1
