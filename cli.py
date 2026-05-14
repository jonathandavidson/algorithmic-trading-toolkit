#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

from dotenv import load_dotenv

from lib.commands.collection import cmd_collection, cmd_collection_add, cmd_collection_init, cmd_collection_list, cmd_collection_remove, cmd_collection_run, cmd_collection_update
from lib.commands.database import cmd_database, cmd_database_add, cmd_database_list, cmd_database_remove, cmd_database_test, cmd_database_update
from lib.commands.datasource import cmd_datasource, cmd_datasource_add, cmd_datasource_list, cmd_datasource_remove, cmd_datasource_test, cmd_datasource_update
from lib.commands.version import cmd_version


def _iso8601(value):
    try:
        datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid ISO 8601 datetime: {value!r}")
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hdc",
        description="Historical Data Collector CLI",
    )
    parser.add_argument("--version", dest="show_version", action="store_true", help="show version")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = False

    database = subparsers.add_parser("database", help="manage databases")
    database.set_defaults(func=cmd_database, database_parser=database)
    database_subparsers = database.add_subparsers(dest="database_command", metavar="COMMAND")

    database_add = database_subparsers.add_parser("add", help="add a database")
    database_add.add_argument("--name", required=True, help="connection name")
    database_add.add_argument("--type", dest="db_type", required=True, help="database type")
    database_add.add_argument("--username", required=True, help="database username")
    database_add.add_argument("--password", required=True, help="database password")
    database_add.add_argument("--host", required=True, help="database host")
    database_add.add_argument("--port", type=int, required=True, help="database port")
    database_add.add_argument("--dbname", required=True, help="database name")
    database_add.set_defaults(func=cmd_database_add)

    database_update = database_subparsers.add_parser("update", help="update a database")
    database_update.add_argument("--name", required=True, help="connection name")
    database_update.add_argument("--type", dest="db_type", default=None, help="database type")
    database_update.add_argument("--username", default=None, help="database username")
    database_update.add_argument("--password", default=None, help="database password")
    database_update.add_argument("--host", default=None, help="database host")
    database_update.add_argument("--port", type=int, default=None, help="database port")
    database_update.add_argument("--dbname", default=None, help="database name")
    database_update.set_defaults(func=cmd_database_update)

    database_list = database_subparsers.add_parser("list", help="list databases")
    database_list.set_defaults(func=cmd_database_list)

    database_remove = database_subparsers.add_parser("remove", help="remove a database")
    database_remove.add_argument("--name", required=True, help="database name")
    database_remove.set_defaults(func=cmd_database_remove)

    database_test = database_subparsers.add_parser("test", help="test database connection")
    database_test.add_argument("--name", required=True, help="database name")
    database_test.set_defaults(func=cmd_database_test)

    datasource = subparsers.add_parser("datasource", help="manage datasources")
    datasource.set_defaults(func=cmd_datasource, datasource_parser=datasource)
    datasource_subparsers = datasource.add_subparsers(dest="datasource_command", metavar="COMMAND")

    datasource_add = datasource_subparsers.add_parser("add", help="add a datasource")
    datasource_add.add_argument("--name", required=True, help="datasource name")
    datasource_add.add_argument("--type", dest="datasource_type", required=True, choices=["alpaca"], help="datasource type")
    datasource_add.add_argument("--apiKey", dest="api_key", required=True, help="API key")
    datasource_add.add_argument("--apiSecret", dest="api_secret", required=True, help="API secret")
    datasource_add.set_defaults(func=cmd_datasource_add)

    datasource_update = datasource_subparsers.add_parser("update", help="update a datasource")
    datasource_update.add_argument("--name", required=True, help="datasource name")
    datasource_update.add_argument("--type", dest="datasource_type", default=None, choices=["alpaca"], help="datasource type")
    datasource_update.add_argument("--apiKey", dest="api_key", default=None, help="API key")
    datasource_update.add_argument("--apiSecret", dest="api_secret", default=None, help="API secret")
    datasource_update.set_defaults(func=cmd_datasource_update)

    datasource_list = datasource_subparsers.add_parser("list", help="list datasources")
    datasource_list.set_defaults(func=cmd_datasource_list)

    datasource_test = datasource_subparsers.add_parser("test", help="test datasource authentication")
    datasource_test.add_argument("--name", required=True, help="datasource name")
    datasource_test.set_defaults(func=cmd_datasource_test)

    datasource_remove = datasource_subparsers.add_parser("remove", help="remove a datasource")
    datasource_remove.add_argument("--name", required=True, help="datasource name")
    datasource_remove.set_defaults(func=cmd_datasource_remove)

    collection = subparsers.add_parser("collection", help="manage collections")
    collection.set_defaults(func=cmd_collection, collection_parser=collection)
    collection_subparsers = collection.add_subparsers(dest="collection_command", metavar="COMMAND")

    collection_add = collection_subparsers.add_parser("add", help="add a collection")
    collection_add.add_argument("--name", required=True, help="collection name")
    collection_add.add_argument("--database", required=True, help="database name")
    collection_add.add_argument("--datasource", required=True, help="datasource name")
    collection_add.add_argument("--type", required=True, choices=["historical-bars"], help="collection type")
    collection_add.add_argument("--frequency", choices=["1m", "1d"], help="data frequency")
    collection_add.add_argument("--start", required=True, type=_iso8601, help="start datetime (ISO 8601)")
    collection_add.add_argument("--end", type=_iso8601, help="end datetime (ISO 8601)")
    collection_add.add_argument("--symbols", type=lambda s: [x.strip() for x in s.split(",")], help="comma-separated list of symbols")
    collection_add.set_defaults(func=cmd_collection_add)

    collection_update = collection_subparsers.add_parser("update", help="update a collection")
    collection_update.add_argument("--name", required=True, help="collection name")
    collection_update.add_argument("--database", default=None, help="database name")
    collection_update.add_argument("--datasource", default=None, help="datasource name")
    collection_update.add_argument("--type", default=None, choices=["historical-bars"], help="collection type")
    collection_update.add_argument("--frequency", default=None, choices=["1m", "1d"], help="data frequency")
    collection_update.add_argument("--start", default=None, type=_iso8601, help="start datetime (ISO 8601)")
    collection_update.add_argument("--end", default=None, type=_iso8601, help="end datetime (ISO 8601)")
    collection_update.add_argument("--symbols", default=None, type=lambda s: [x.strip() for x in s.split(",")], help="comma-separated list of symbols")
    collection_update.set_defaults(func=cmd_collection_update)

    collection_list = collection_subparsers.add_parser("list", help="list collections")
    collection_list.set_defaults(func=cmd_collection_list)

    collection_remove = collection_subparsers.add_parser("remove", help="remove a collection")
    collection_remove.add_argument("--name", required=True, help="collection name")
    collection_remove.set_defaults(func=cmd_collection_remove)

    collection_init = collection_subparsers.add_parser("init", help="initialize a collection")
    collection_init.add_argument("--name", required=True, help="collection name")
    collection_init.set_defaults(func=cmd_collection_init)

    collection_run = collection_subparsers.add_parser("run", help="run a collection")
    collection_run.add_argument("--name", required=True, help="collection name")
    collection_run.set_defaults(func=cmd_collection_run)

    return parser


def main():
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    if args.show_version:
        cmd_version(args)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
