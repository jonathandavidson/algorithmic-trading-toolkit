from argparse import Namespace

from lib.services.configuration.collection import CollectionConfiguration, CollectionConfigurationService, CollectionNotFoundError, DatabaseNotFoundError, QueryNotFoundError
from lib.services.configuration.database import DatabaseConfigurationService

_service = CollectionConfigurationService()
_db_service = DatabaseConfigurationService()


def cmd_collection_add(args: Namespace) -> None:
    try:
        _service.add(CollectionConfiguration(
            name=args.name,
            database=args.database,
            datasource=args.datasource,
            query=args.query,
            type=args.type,
            start=args.start,
            frequency=args.frequency,
            end=args.end,
            symbols=args.symbols,
        ))
        print(f"Collection '{args.name}' added.")
    except QueryNotFoundError as e:
        print(f"Query '{e.args[0]}' not found.")
    except ValueError as e:
        print(e)


def cmd_collection_list(args: Namespace) -> None:
    collections = _service.list()
    if not collections:
        print("No collections configured.")
        return
    for c in collections:
        parts = [
            f"name={c.name}",
            f"type={c.type}",
            f"database={c.database}",
            f"datasource={c.datasource}",
            f"start={c.start.isoformat()}",
        ]
        if c.query is not None:
            parts.append(f"query={c.query}")
        if c.frequency is not None:
            parts.append(f"frequency={c.frequency.value}")
        if c.end is not None:
            parts.append(f"end={c.end.isoformat()}")
        if c.symbols is not None:
            parts.append(f"symbols={','.join(c.symbols)}")
        print("  ".join(parts))


def cmd_collection_update(args: Namespace) -> None:
    updates: dict = {}
    if args.database is not None:
        updates["database"] = args.database
    if args.datasource is not None:
        updates["datasource"] = args.datasource
    if args.query is not None:
        updates["query"] = args.query
    if args.type is not None:
        updates["type"] = args.type
    if args.start is not None:
        updates["start"] = args.start
    if args.end is not None:
        updates["end"] = args.end
    if args.frequency is not None:
        updates["frequency"] = args.frequency
    if args.symbols is not None:
        updates["symbols"] = args.symbols
    if not updates:
        print("No fields to update.")
        return
    try:
        _service.update(args.name, updates)
        print(f"Collection '{args.name}' updated.")
    except QueryNotFoundError as e:
        print(f"Query '{e.args[0]}' not found.")
    except CollectionNotFoundError:
        print(f"Collection '{args.name}' not found.")


def cmd_collection_remove(args: Namespace) -> None:
    if not any(c.name == args.name for c in _service.list()):
        print(f"Collection '{args.name}' not found.")
        return
    answer = input(f"Remove collection '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    _service.remove(args.name)
    print(f"Collection '{args.name}' removed.")


def cmd_collection_init(args: Namespace) -> None:
    collection = next((c for c in _service.list() if c.name == args.name), None)
    if collection is None:
        print(f"Collection '{args.name}' not found.")
        return
    db = next((d for d in _db_service.list() if d.name == collection.database), None)
    if db is None:
        print(f"Database '{collection.database}' not found.")
        return
    answer = input(
        f"Create tables in database '{db.name}' ({db.host}:{db.port}/{db.dbname})? "
        f"Any existing tables will be dropped and recreated — back up data to avoid losing it. [y/N] "
    )
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    _service.init(args.name)
    print("Tables created.")


def cmd_collection_run(args: Namespace) -> None:
    try:
        count = _service.run(args.name)
        print(f"Inserted {count} records.")
    except CollectionNotFoundError:
        print(f"Collection '{args.name}' not found.")
    except DatabaseNotFoundError as e:
        print(f"Database '{e.args[0]}' not found.")
    except Exception as e:
        print(f"Error running collection: {str(e)}")


def cmd_collection(args: Namespace) -> None:
    if not hasattr(args, "collection_command") or args.collection_command is None:
        args.collection_parser.print_help()
