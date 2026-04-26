# Historical Data Collector

A command-line tool for collecting historical data.

## Setup

### Create a virtual environment (recommended)

Create the virtual environment (first time setup)
```bash
python -m venv .venv
```

Activate the virtual environment
```bash
source .venv/bin/activate
```

### Install

```bash
pip install -e .
```

This installs the `hdc` command into the virtual environment.

### Install test dependencies

```bash
pip install -r test/requirements.txt
```

## Usage

```bash
hdc <command>
```

### Commands

**collect** — collect historical data

```bash
hdc collect
```

**configure** — configure the tool

```bash
hdc configure add database --name <name> --type <type> --username <user> \
    --password <pass> --host <host> --port <port> --dbname <dbname> [--default]

hdc configure list database

hdc configure remove database --name <name>

hdc configure test database
```

**version** — show the current version

```bash
hdc --version
```

## Help

```bash
hdc --help
hdc <command> --help
```
