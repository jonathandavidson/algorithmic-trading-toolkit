from argparse import Namespace

from lib.services.configuration.query import QueryConfiguration, QueryConfigurationService, QueryNotFoundError

_service = QueryConfigurationService()


def cmd_query_add(args: Namespace) -> None:
    try:
        _service.add(QueryConfiguration(name=args.name))
        print(f"Query '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_query_list(args: Namespace) -> None:
    queries = _service.list()
    if not queries:
        print("No queries configured.")
        return
    for q in queries:
        print(f"name={q.name}")


def cmd_query_update(args: Namespace) -> None:
    updates: dict = {}
    if not updates:
        print("No fields to update.")
        return
    try:
        _service.update(args.name, updates)
        print(f"Query '{args.name}' updated.")
    except QueryNotFoundError:
        print(f"Query '{args.name}' not found.")


def cmd_query_remove(args: Namespace) -> None:
    if not any(q.name == args.name for q in _service.list()):
        print(f"Query '{args.name}' not found.")
        return
    answer = input(f"Remove query '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    _service.remove(args.name)
    print(f"Query '{args.name}' removed.")


def cmd_query(args: Namespace) -> None:
    if not hasattr(args, "query_command") or args.query_command is None:
        args.query_parser.print_help()
