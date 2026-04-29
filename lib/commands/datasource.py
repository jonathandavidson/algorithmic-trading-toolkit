from argparse import Namespace

import lib.services.datasource as datasource_service


def cmd_datasource_add(args: Namespace) -> None:
    try:
        datasource_service.add(
            name=args.name,
            datasource_type=args.datasource_type,
            api_key=args.api_key,
            api_secret=args.api_secret,
        )
        print(f"Datasource '{args.name}' added.")
    except ValueError as e:
        print(e)


def cmd_datasource(args: Namespace) -> None:
    if not hasattr(args, "datasource_command") or args.datasource_command is None:
        args.datasource_parser.print_help()
