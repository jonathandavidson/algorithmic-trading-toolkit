from argparse import Namespace

import lib.services.collection as collection_service
import lib.services.database as database_service
from lib.services.collection import CollectionNotFoundError, CollectionConfiguration, DatabaseNotFoundError


def cmd_collection_add(args: Namespace) -> None:
    try:
        collection_service.add(CollectionConfiguration(
            name=args.name,
            database=args.database,
            type=args.type,
            start=args.start,
            frequency=args.frequency,
            end=args.end,
        ))
        print(f"Collection '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_collection_list(args: Namespace) -> None:
    collections = collection_service.list()
    if not collections:
        print("No collections configured.")
        return
    for c in collections:
        parts = [
            f"name={c['name']}",
            f"database={c['database']}",
            f"type={c['type']}",
            f"start={c['start']}",
        ]
        if "frequency" in c:
            parts.append(f"frequency={c['frequency']}")
        if "end" in c:
            parts.append(f"end={c['end']}")
        print("  ".join(parts))


def cmd_collection_remove(args: Namespace) -> None:
    if not any(c["name"] == args.name for c in collection_service.list()):
        print(f"Collection '{args.name}' not found.")
        return
    answer = input(f"Remove collection '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    collection_service.remove(args.name)
    print(f"Collection '{args.name}' removed.")


def cmd_collection_init(args: Namespace) -> None:
    collection = next((c for c in collection_service.list() if c["name"] == args.name), None)
    if collection is None:
        print(f"Collection '{args.name}' not found.")
        return
    db = next((d for d in database_service.list() if d["name"] == collection["database"]), None)
    if db is None:
        print(f"Database '{collection['database']}' not found.")
        return
    answer = input(
        f"Create tables in database '{db['name']}' ({db['host']}:{db['port']}/{db['dbname']})? "
        f"Any existing tables will be dropped and recreated — back up data to avoid losing it. [y/N] "
    )
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    collection_service.init(args.name)
    print("Tables created.")


def cmd_collection_run(args: Namespace) -> None:
    try:
        count = collection_service.run(args.name)
        print(f"Inserted {count} records.")
    except CollectionNotFoundError:
        print(f"Collection '{args.name}' not found.")
    except DatabaseNotFoundError as e:
        print(f"Database '{e.args[0]}' not found.")


def cmd_collection(args: Namespace) -> None:
    if not hasattr(args, "collection_command") or args.collection_command is None:
        args.collection_parser.print_help()
