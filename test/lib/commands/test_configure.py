import argparse

from lib.commands.configure import cmd_configure


def test_cmd_configure_no_subcommand_prints_help(capsys):
    parser = argparse.ArgumentParser()
    args = parser.parse_args([])
    args.configure_command = None
    args.configure_parser = parser
    cmd_configure(args)
    assert capsys.readouterr().out != ""
