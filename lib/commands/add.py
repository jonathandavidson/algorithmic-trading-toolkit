from lib.config import load_config, save_config


def cmd_add_database(args):
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


def cmd_add(args):
    if not hasattr(args, "add_command") or args.add_command is None:
        args.add_parser.print_help()
