import os

import yaml

CONFIG_PATH = ".config/hdc.config.yaml"


def _load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def _save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def cmd_configure_add_database(args):
    config = _load_config()
    databases = config.setdefault("databases", [])
    if any(db["name"] == args.name for db in databases):
        print(f"Database '{args.name}' already exists.")
        return
    databases.append({
        "name": args.name,
        "type": args.db_type,
        "username": args.username,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
    })
    _save_config(config)
    print(f"Database '{args.name}' added.")


def cmd_configure_list_database(args):
    databases = _load_config().get("databases", [])
    if not databases:
        print("No databases configured.")
        return
    for db in databases:
        print(
            f"name={db['name']}  type={db['type']}  host={db['host']}  "
            f"port={db['port']}  dbname={db['dbname']}  "
            f"username={db['username']}  password=********"
        )


def cmd_configure_remove_database(args):
    config = _load_config()
    databases = config.get("databases", [])
    if not any(db["name"] == args.name for db in databases):
        print(f"Database '{args.name}' not found.")
        return
    answer = input(f"Remove database '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    config["databases"] = [db for db in databases if db["name"] != args.name]
    _save_config(config)
    print(f"Database '{args.name}' removed.")


def cmd_configure(args):
    if not hasattr(args, "configure_command") or args.configure_command is None:
        args.configure_parser.print_help()
