import pytest
import yaml
from unittest.mock import patch

import cli


def test_build_parser_has_collect_subcommand():
    parser = cli.build_parser()
    args = parser.parse_args(["collect"])
    assert args.command == "collect"


def test_build_parser_version_flag():
    parser = cli.build_parser()
    args = parser.parse_args(["--version"])
    assert args.show_version is True


def test_main_version_flag(capsys):
    with patch("sys.argv", ["hdc", "--version"]):
        cli.main()
    assert capsys.readouterr().out.strip() == "historical-data-collector 0.1.0"


def test_main_collect(capsys):
    with patch("sys.argv", ["hdc", "collect"]):
        cli.main()
    assert capsys.readouterr().out.strip() == "collect: not implemented"


def test_main_no_args_exits(capsys):
    with patch("sys.argv", ["hdc"]):
        with pytest.raises(SystemExit) as exc:
            cli.main()
    assert exc.value.code == 1
