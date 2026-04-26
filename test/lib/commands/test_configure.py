from lib.commands.configure import cmd_configure


def test_cmd_configure_is_noop(capsys):
    cmd_configure(None)
    assert capsys.readouterr().out == ""
