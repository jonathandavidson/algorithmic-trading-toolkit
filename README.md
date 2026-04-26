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

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python cli.py <command>
```

### Commands

**collect** — collect historical data

```bash
python cli.py collect
```

**configure** — configure the tool

```bash
python cli.py configure
python cli.py configure add database
```

**version** — show the current version

```bash
python cli.py --version
```

## Help

```bash
python cli.py --help
python cli.py <command> --help
```
