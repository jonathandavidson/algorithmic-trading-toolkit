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

**run** — run a collection

```bash
hdc run collection --name <name>
```

**add** — add resources

```bash
hdc add database --name <name> --type <type> --username <user> \
    --password <pass> --host <host> --port <port> --dbname <dbname>
```

**configure** — configure the tool

```bash
hdc configure add collection --name <name> --database <db> --type historical-bars \
    --start <ISO8601> [--frequency 1m|1d] [--end <ISO8601>]

hdc configure list database

hdc configure list collection

hdc configure remove database --name <name>

hdc configure remove collection --name <name>

hdc configure init collection --name <name>

hdc configure test database --name <name>
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
