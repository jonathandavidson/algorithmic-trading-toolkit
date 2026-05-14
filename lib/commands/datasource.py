from argparse import Namespace

from lib.services.configuration.datasource import DatasourceConfiguration, DatasourceConfigurationService

_service = DatasourceConfigurationService()


def cmd_datasource_add(args: Namespace) -> None:
    try:
        _service.add(DatasourceConfiguration(
            name=args.name,
            type=args.datasource_type,
            api_key=args.api_key,
            api_secret=args.api_secret,
        ))
        print(f"Datasource '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_datasource_list(args: Namespace) -> None:
    datasources = _service.list()
    if not datasources:
        print("No datasources configured.")
        return
    for ds in datasources:
        print(f"name={ds.name}  type={ds.type}  api_key={ds.api_key}  api_secret=********")


def cmd_datasource_test(args: Namespace) -> None:
    try:
        _service.test(args.name)
        print(f"Authentication to '{args.name}' successful.")
    except KeyError:
        print(f"Datasource '{args.name}' not found.")
    except Exception as e:
        print(f"Authentication to '{args.name}' failed: {e}")


def cmd_datasource_update(args: Namespace) -> None:
    updates: dict = {}
    if args.datasource_type is not None:
        updates["type"] = args.datasource_type
    if args.api_key is not None:
        updates["api_key"] = args.api_key
    if args.api_secret is not None:
        updates["api_secret"] = args.api_secret
    if not updates:
        print("No fields to update.")
        return
    try:
        _service.update(args.name, updates)
        print(f"Datasource '{args.name}' updated.")
    except KeyError:
        print(f"Datasource '{args.name}' not found.")


def cmd_datasource_remove(args: Namespace) -> None:
    if not any(ds.name == args.name for ds in _service.list()):
        print(f"Datasource '{args.name}' not found.")
        return
    answer = input(f"Remove datasource '{args.name}'? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    _service.remove(args.name)
    print(f"Datasource '{args.name}' removed.")


def cmd_datasource(args: Namespace) -> None:
    if not hasattr(args, "datasource_command") or args.datasource_command is None:
        args.datasource_parser.print_help()
