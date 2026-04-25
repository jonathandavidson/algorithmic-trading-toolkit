#!/usr/bin/env python3
import argparse
import sys


def cmd_hello(args):
    name = args.name or "World"
    print(f"Hello, {name}!")


def cmd_echo(args):
    print(" ".join(args.text))


def cmd_version(args):
    print("historical-data-collector 0.1.0")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hdc",
        description="Historical Data Collector CLI",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    hello = subparsers.add_parser("hello", help="print a greeting")
    hello.add_argument("--name", "-n", help="name to greet")
    hello.set_defaults(func=cmd_hello)

    echo = subparsers.add_parser("echo", help="echo text back")
    echo.add_argument("text", nargs="+", help="text to echo")
    echo.set_defaults(func=cmd_echo)

    version = subparsers.add_parser("version", help="show version")
    version.set_defaults(func=cmd_version)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
