from argparse import Namespace

from lib.services.configuration.collection import CollectionConfiguration, CollectionConfigurationService, CollectionNotFoundError, DatabaseNotFoundError
from lib.services.configuration.database import DatabaseConfigurationService

_service = CollectionConfigurationService()
_db_service = DatabaseConfigurationService()


def cmd_collection_add(args: Namespace) -> None:
    try:
        _service.add(CollectionConfiguration(
            name=args.name,
            database=args.database,
            datasource=args.datasource,
            type=args.type,
            start=args.start,
            frequency=args.frequency,
            end=args.end,
        ))
        print(f"Collection '{args.name}' added.")
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
        if c.frequency is not None:
            parts.append(f"frequency={c.frequency}")
        if c.end is not None:
            parts.append(f"end={c.end.isoformat()}")
        print("  ".join(parts))


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
