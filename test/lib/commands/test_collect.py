from lib.commands.collect import cmd_collect


def test_cmd_collect_prints_not_implemented(capsys):
    cmd_collect(None)
    assert capsys.readouterr().out.strip() == "collect: not implemented"
