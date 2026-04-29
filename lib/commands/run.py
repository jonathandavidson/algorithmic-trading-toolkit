def cmd_run_collection(args):
    print("run collection: not implemented")


def cmd_run(args):
    if not hasattr(args, "run_command") or args.run_command is None:
        args.run_parser.print_help()
