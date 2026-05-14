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

## Configuration

### HDC_SECRET

`HDC_SECRET` is a required environment variable used to encrypt sensitive credentials (database passwords, API secrets) stored in the configuration. You must set it before adding or using any database or datasource.

Generate a strong secret and export it in your shell:

```bash
export HDC_SECRET="your-strong-secret-here"
```

To make it permanent, add the export to your shell profile (e.g. `~/.bashrc`, `~/.zshrc`):

```bash
echo 'export HDC_SECRET="your-strong-secret-here"' >> ~/.bashrc
source ~/.bashrc
```

Alternatively, store it in a `.env` file at the project root (this file is gitignored):

```
HDC_SECRET=your-strong-secret-here
```

`hdc` loads `.env` automatically on startup.

> **Important:** Use the same `HDC_SECRET` value every time. If it changes, previously stored credentials will not be decryptable and you will need to remove and re-add your databases and datasources.

## Usage

```bash
hdc <command>
```

### Commands

**datasource** — manage datasources

```bash
hdc datasource add --name <name> --type alpaca --apiKey <key> --apiSecret <secret>

hdc datasource update --name <name> [--type alpaca] [--apiKey <key>] [--apiSecret <secret>]

hdc datasource list

hdc datasource test --name <name>

hdc datasource remove --name <name>
```

**database** — manage databases

```bash
hdc database add --name <name> --type <type> --username <user> \
    --password <pass> --host <host> --port <port> --dbname <dbname>

hdc database update --name <name> [--type <type>] [--username <user>] \
    [--password <pass>] [--host <host>] [--port <port>] [--dbname <dbname>]

hdc database list

hdc database remove --name <name>

hdc database test --name <name>
```

**collection** — manage collections

```bash
hdc collection add --name <name> --database <db> --type historical-bars \
    --start <ISO8601> [--frequency 1m|1d] [--end <ISO8601>]

hdc collection update --name <name> [--database <db>] [--datasource <ds>] \
    [--type historical-bars] [--start <ISO8601>] [--frequency 1m|1d] \
    [--end <ISO8601>] [--symbols <sym1,sym2,...>]

hdc collection list

hdc collection remove --name <name>

hdc collection init --name <name>

hdc collection run --name <name>
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
