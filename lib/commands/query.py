from argparse import Namespace

from lib.services.configuration.query import QueryConfiguration, QueryConfigurationService, QueryNotFoundError
from lib.services.configuration.system import SystemConfigurationService
from lib.services.configuration.type.query.factory import get_query_type_class

_service = QueryConfigurationService()


def cmd_query_add(args: Namespace) -> None:
    try:
        SystemConfigurationService('query_types').get_one(args.type)
    except KeyError:
        print(f"Unknown query type '{args.type}'.")
        return

    type_class = get_query_type_class(args.type)

    kwargs: dict = {}
    if args.symbols is not None:
        kwargs['symbols'] = args.symbols
    if args.frequency is not None:
        kwargs['frequency'] = args.frequency
    if args.start is not None:
        kwargs['start'] = args.start
    if args.end is not None:
        kwargs['end'] = args.end

    try:
        type_instance = type_class(**kwargs)
    except (TypeError, ValueError) as e:
        print(f"Invalid query configuration: {e}")
        return

    type_fields = type_instance.to_dict()
    try:
        _service.add(QueryConfiguration(name=args.name, type=args.type, **type_fields))
        print(f"Query '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_query_list(args: Namespace) -> None:
    queries = _service.list()
    if not queries:
        print("No queries configured.")
        return
    for q in queries:
        fields = ", ".join(f"{k}={v}" for k, v in q.to_dict().items())
        print(fields)


def cmd_query_update(args: Namespace) -> None:
    raw_updates: dict = {}
    if args.symbols is not None:
        raw_updates['symbols'] = args.symbols
    if args.frequency is not None:
        raw_updates['frequency'] = args.frequency
    if args.start is not None:
        raw_updates['start'] = args.start
    if args.end is not None:
        raw_updates['end'] = args.end

    if not raw_updates:
        print("No fields to update.")
        return

    try:
        existing = _service.get_one(args.name)
    except QueryNotFoundError:
        print(f"Query '{args.name}' not found.")
        return

    merged = existing.to_dict()
    merged.update(raw_updates)

    type_class = get_query_type_class(existing.type)
    type_kwargs = {k: v for k, v in merged.items() if k not in ('name', 'type')}
    try:
        type_instance = type_class(**type_kwargs)
    except (TypeError, ValueError) as e:
        print(f"Invalid query configuration: {e}")
        return

    validated = type_instance.to_dict()
    try:
        _service.update(args.name, validated)
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
