def cmd_configure_add_database(args):
    pass


def cmd_configure(args):
    if not hasattr(args, "configure_command") or args.configure_command is None:
        args.configure_parser.print_help()
