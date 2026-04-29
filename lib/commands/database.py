from argparse import Namespace

import lib.services.database as database_service


def cmd_database_add(args: Namespace) -> None:
    try:
        database_service.add(
            name=args.name,
            db_type=args.db_type,
            username=args.username,
            password=args.password,
            host=args.host,
            port=args.port,
            dbname=args.dbname,
        )
        print(f"Database '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_database_list(args: Namespace) -> None:
    databases = database_service.list()
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
    if not any(db["name"] == args.name for db in database_service.list()):
        print(f"Database '{args.name}' not found.")
        return
    answer = input(f"Remove database '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    database_service.remove(args.name)
    print(f"Database '{args.name}' removed.")


def cmd_database_test(args: Namespace) -> None:
    try:
        database_service.test(args.name)
        print(f"Connection to '{args.name}' successful.")
    except KeyError:
        print(f"Database '{args.name}' not found.")
    except Exception as e:
        print(f"Connection to '{args.name}' failed: {e}")


def cmd_database(args: Namespace) -> None:
    if not hasattr(args, "database_command") or args.database_command is None:
        args.database_parser.print_help()
