# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Virtual environment

Always run `python`, `pip`, and `pytest` from the project virtual environment:

```bash
.venv/bin/python
.venv/bin/pip
.venv/bin/pytest
```

Never use bare `python`, `pip`, or `pytest` commands — they will resolve to the system interpreter and may not have the project dependencies installed.

## Running the CLI

```bash
.venv/bin/hdc <command>
.venv/bin/hdc --help
```

## Running tests

```bash
.venv/bin/pytest                        # all tests with coverage report
.venv/bin/pytest test/test_cli.py       # single file
```

Coverage runs automatically via `setup.cfg` and reports missing lines.

## Architecture

`cli.py` is the single entrypoint. It uses Python's `argparse` with subparsers — each subcommand has a dedicated `cmd_<name>` handler function and is registered in `build_parser()`. `main()` dispatches to the handler via `args.func(args)`.

## README maintenance

Whenever the CLI interface changes (new subcommands, removed subcommands, changed flags or arguments), update `README.md` to reflect the new usage.
