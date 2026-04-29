from lib.config import load_config, save_config
from lib.database import get_engine
from lib.models.base import Base
import lib.models.historical_bars  # registers HistoricalBar with Base.metadata


def cmd_configure_add_collection(args):
    config = load_config()
    collections = config.setdefault("collections", [])
    if any(c["name"] == args.name for c in collections):
        print(f"Collection '{args.name}' already exists.")
        return
    entry = {
        "name": args.name,
        "database": args.database,
        "type": args.type,
        "start": args.start,
    }
    if args.frequency is not None:
        entry["frequency"] = args.frequency
    if args.end is not None:
        entry["end"] = args.end
    collections.append(entry)
    save_config(config)
    print(f"Collection '{args.name}' added.")


def cmd_configure_init_collection(args):
    config = load_config()
    collections = config.get("collections", [])
    collection = next((c for c in collections if c["name"] == args.name), None)
    if collection is None:
        print(f"Collection '{args.name}' not found.")
        return
    databases = config.get("databases", [])
    db = next((d for d in databases if d["name"] == collection["database"]), None)
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
    engine = get_engine(db)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables created.")


def cmd_configure_list_collection(args):
    collections = load_config().get("collections", [])
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


def cmd_configure_remove_collection(args):
    config = load_config()
    collections = config.get("collections", [])
    if not any(c["name"] == args.name for c in collections):
        print(f"Collection '{args.name}' not found.")
        return
    answer = input(f"Remove collection '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    config["collections"] = [c for c in collections if c["name"] != args.name]
    save_config(config)
    print(f"Collection '{args.name}' removed.")



def cmd_configure(args):
    if not hasattr(args, "configure_command") or args.configure_command is None:
        args.configure_parser.print_help()
