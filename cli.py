#!/usr/bin/env python3
import argparse
import sys

from lib.commands.collect import cmd_collect
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
