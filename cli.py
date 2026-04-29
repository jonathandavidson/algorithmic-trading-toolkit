#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime

from lib.commands.configure import cmd_configure, cmd_configure_add_collection, cmd_configure_init_collection, cmd_configure_list_collection, cmd_configure_remove_collection
from lib.commands.database import cmd_database, cmd_database_add, cmd_database_list, cmd_database_remove, cmd_database_test
from lib.commands.run import cmd_run, cmd_run_collection
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

    database_list = database_subparsers.add_parser("list", help="list databases")
    database_list.set_defaults(func=cmd_database_list)

    database_remove = database_subparsers.add_parser("remove", help="remove a database")
    database_remove.add_argument("--name", required=True, help="database name")
    database_remove.set_defaults(func=cmd_database_remove)

    database_test = database_subparsers.add_parser("test", help="test database connection")
    database_test.add_argument("--name", required=True, help="database name")
    database_test.set_defaults(func=cmd_database_test)

    run = subparsers.add_parser("run", help="run a collection")
    run.set_defaults(func=cmd_run, run_parser=run)
    run_subparsers = run.add_subparsers(dest="run_command", metavar="COMMAND")

    run_collection = run_subparsers.add_parser("collection", help="run a collection")
    run_collection.add_argument("--name", required=True, help="collection name")
    run_collection.set_defaults(func=cmd_run_collection)

    configure = subparsers.add_parser("configure", help="configure the tool")
    configure.set_defaults(func=cmd_configure, configure_parser=configure)
    configure_subparsers = configure.add_subparsers(dest="configure_command", metavar="COMMAND")

    configure_add = configure_subparsers.add_parser("add", help="add configuration")
    configure_add_subparsers = configure_add.add_subparsers(dest="configure_add_command", metavar="COMMAND")
    configure_add.set_defaults(func=lambda args: configure_add.print_help())

    configure_add_collection = configure_add_subparsers.add_parser("collection", help="add a collection")
    configure_add_collection.add_argument("--name", required=True, help="collection name")
    configure_add_collection.add_argument("--database", required=True, help="database name")
    configure_add_collection.add_argument("--type", required=True, choices=["historical-bars"], help="collection type")
    configure_add_collection.add_argument("--frequency", choices=["1m", "1d"], help="data frequency")
    configure_add_collection.add_argument("--start", required=True, type=_iso8601, help="start datetime (ISO 8601)")
    configure_add_collection.add_argument("--end", type=_iso8601, help="end datetime (ISO 8601)")
    configure_add_collection.set_defaults(func=cmd_configure_add_collection)

    configure_list = configure_subparsers.add_parser("list", help="list configuration")
    configure_list_subparsers = configure_list.add_subparsers(dest="configure_list_command", metavar="COMMAND")
    configure_list.set_defaults(func=lambda args: configure_list.print_help())

    configure_list_collection = configure_list_subparsers.add_parser("collection", help="list collections")
    configure_list_collection.set_defaults(func=cmd_configure_list_collection)

    configure_remove = configure_subparsers.add_parser("remove", help="remove configuration")
    configure_remove_subparsers = configure_remove.add_subparsers(dest="configure_remove_command", metavar="COMMAND")
    configure_remove.set_defaults(func=lambda args: configure_remove.print_help())

    configure_remove_collection = configure_remove_subparsers.add_parser("collection", help="remove a collection")
    configure_remove_collection.add_argument("--name", required=True, help="collection name")
    configure_remove_collection.set_defaults(func=cmd_configure_remove_collection)

    configure_init = configure_subparsers.add_parser("init", help="initialize configuration")
    configure_init_subparsers = configure_init.add_subparsers(dest="configure_init_command", metavar="COMMAND")
    configure_init.set_defaults(func=lambda args: configure_init.print_help())

    configure_init_collection = configure_init_subparsers.add_parser("collection", help="initialize a collection")
    configure_init_collection.add_argument("--name", required=True, help="collection name")
    configure_init_collection.set_defaults(func=cmd_configure_init_collection)

    return parser


def main():
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
