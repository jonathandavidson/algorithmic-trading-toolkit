from lib.commands.version import cmd_version


def test_cmd_version_prints_version(capsys):
    cmd_version(None)
    assert capsys.readouterr().out.strip() == "historical-data-collector 0.1.0"
