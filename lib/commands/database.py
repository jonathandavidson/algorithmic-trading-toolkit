from argparse import Namespace

from lib.config import load_config, save_config
from lib.database import connect


def cmd_database_add(args: Namespace) -> None:
    config = load_config()
    databases = config.setdefault("databases", [])
    if any(db["name"] == args.name for db in databases):
        print(f"Database '{args.name}' already exists.")
        return
    is_first = len(databases) == 0
    entry = {
        "name": args.name,
        "type": args.db_type,
        "username": args.username,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
    }
    if is_first:
        entry["default"] = True
    databases.append(entry)
    save_config(config)
    print(f"Database '{args.name}' added.")


def cmd_database_list(args: Namespace) -> None:
    databases = load_config().get("databases", [])
    if not databases:
        print("No databases configured.")
        return
    for db in databases:
        default_flag = "  default=true" if db.get("default") else ""
        print(
            f"name={db['name']}  type={db['type']}  host={db['host']}  "
            f"port={db['port']}  dbname={db['dbname']}  "
            f"username={db['username']}  password=********{default_flag}"
        )


def cmd_database_remove(args: Namespace) -> None:
    config = load_config()
    databases = config.get("databases", [])
    if not any(db["name"] == args.name for db in databases):
        print(f"Database '{args.name}' not found.")
        return
    answer = input(f"Remove database '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    config["databases"] = [db for db in databases if db["name"] != args.name]
    save_config(config)
    print(f"Database '{args.name}' removed.")


def cmd_database_test(args: Namespace) -> None:
    databases = load_config().get("databases", [])
    db = next((d for d in databases if d["name"] == args.name), None)
    if db is None:
        print(f"Database '{args.name}' not found.")
        return
    try:
        with connect(db):
            pass
        print(f"Connection to '{db['name']}' successful.")
    except Exception as e:
        print(f"Connection to '{db['name']}' failed: {e}")


def cmd_database(args: Namespace) -> None:
    if not hasattr(args, "database_command") or args.database_command is None:
        args.database_parser.print_help()
