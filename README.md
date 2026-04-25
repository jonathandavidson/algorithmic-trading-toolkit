# Historical Data Collector

A command-line tool for collecting historical data.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Usage

```bash
python cli.py <command>
```

### Commands

**hello** — print a greeting

```bash
python cli.py hello
python cli.py hello --name Alice
```

**echo** — echo text back

```bash
python cli.py echo hello world
```

**version** — show the current version

```bash
python cli.py version
```

## Help

```bash
python cli.py --help
python cli.py <command> --help
```
