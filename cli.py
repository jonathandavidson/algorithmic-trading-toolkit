#!/usr/bin/env python3
import argparse
import sys

from lib.commands.collect import cmd_collect
from lib.commands.configure import cmd_configure, cmd_configure_add_database, cmd_configure_list_database
from lib.commands.version import cmd_version


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hdc",
        description="Historical Data Collector CLI",
    )
    parser.add_argument("--version", dest="show_version", action="store_true", help="show version")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = False

    collect = subparsers.add_parser("collect", help="collect historical data")
    collect.set_defaults(func=cmd_collect)

    configure = subparsers.add_parser("configure", help="configure the tool")
    configure.set_defaults(func=cmd_configure, configure_parser=configure)
    configure_subparsers = configure.add_subparsers(dest="configure_command", metavar="COMMAND")

    configure_add = configure_subparsers.add_parser("add", help="add configuration")
    configure_add_subparsers = configure_add.add_subparsers(dest="configure_add_command", metavar="COMMAND")
    configure_add.set_defaults(func=lambda args: configure_add.print_help())

    configure_add_database = configure_add_subparsers.add_parser("database", help="add a database")
    configure_add_database.add_argument("--name", required=True, help="connection name")
    configure_add_database.add_argument("--type", dest="db_type", required=True, help="database type")
    configure_add_database.add_argument("--username", required=True, help="database username")
    configure_add_database.add_argument("--password", required=True, help="database password")
    configure_add_database.add_argument("--host", required=True, help="database host")
    configure_add_database.add_argument("--port", type=int, required=True, help="database port")
    configure_add_database.add_argument("--dbname", required=True, help="database name")
    configure_add_database.set_defaults(func=cmd_configure_add_database)

    configure_list = configure_subparsers.add_parser("list", help="list configuration")
    configure_list_subparsers = configure_list.add_subparsers(dest="configure_list_command", metavar="COMMAND")
    configure_list.set_defaults(func=lambda args: configure_list.print_help())

    configure_list_database = configure_list_subparsers.add_parser("database", help="list databases")
    configure_list_database.set_defaults(func=cmd_configure_list_database)

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
