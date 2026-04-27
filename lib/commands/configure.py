import sqlalchemy

from lib.config import load_config, save_config


def cmd_configure_add_database(args):
    config = load_config()
    databases = config.setdefault("databases", [])
    if any(db["name"] == args.name for db in databases):
        print(f"Database '{args.name}' already exists.")
        return
    is_first = len(databases) == 0
    make_default = is_first or args.set_default
    if make_default:
        for db in databases:
            db.pop("default", None)
    entry = {
        "name": args.name,
        "type": args.db_type,
        "username": args.username,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
    }
    if make_default:
        entry["default"] = True
    databases.append(entry)
    save_config(config)
    print(f"Database '{args.name}' added.")


def cmd_configure_list_database(args):
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


def cmd_configure_remove_database(args):
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


_TYPE_ALIASES = {"postgres": "postgresql"}


def cmd_configure_test_database(args):
    databases = load_config().get("databases", [])
    default_db = next((db for db in databases if db.get("default")), None)
    if default_db is None:
        print("No default database found.")
        return
    dialect = _TYPE_ALIASES.get(default_db["type"], default_db["type"])
    url = sqlalchemy.URL.create(
        drivername=dialect,
        username=default_db["username"],
        password=default_db["password"],
        host=default_db["host"],
        port=default_db["port"],
        database=default_db["dbname"],
    )
    try:
        engine = sqlalchemy.create_engine(url)
        with engine.connect():
            pass
        print(f"Connection to '{default_db['name']}' successful.")
    except Exception as e:
        print(f"Connection to '{default_db['name']}' failed: {e}")


def cmd_configure(args):
    if not hasattr(args, "configure_command") or args.configure_command is None:
        args.configure_parser.print_help()
