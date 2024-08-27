# /source/ui/cli.py

"""
    Command line interface application for the video manager
"""

# Standard library
from argparse import ArgumentParser, HelpFormatter, Namespace

# Local imports
from source.facade.facade import Facade

# Third-party packages
# n/a


def handle_parsed_args(parsed_args: Namespace, session: Facade) -> None:
    if parsed_args.command == 'clear':
        print(f"Clearing all transactions from command buffer")
        session.clear_staged_operations()

    if parsed_args.command == 'commit':
        print("Committing staged operations")
        session.commit_staged_operations()

    elif parsed_args.command == 'export':
        print(f"Exporting collection data to '{parsed_args.path}'")
        session.export_collection_metadata(parsed_args.path)

    elif parsed_args.command == 'fetch':
        print(f"Staging fetch from {parsed_args.plugins}")
        session.stage_update_api_metadata(parsed_args.plugins, parsed_args.filters)

    elif parsed_args.command == 'organize':
        print(f"Staging files for organization at '{parsed_args.path}'")
        session.stage_organize_video_files(parsed_args.destination_folder,
                                           parsed_args.dir_name_format,
                                           parsed_args.filters)

    elif parsed_args.command == 'profile':
        print(f"Switching profile to {parsed_args.name}")
        # facade.set_profile(parsed_args.name)

    elif parsed_args.command == 'scan':
        print(f"Scanning '{parsed_args.path}'")
        session.scan_files_in_path(parsed_args.path)

    elif parsed_args.command == 'undo':
        print(f"Undoing last commit")
        session.undo_transaction()

    elif parsed_args.command == 'view':
        print(f"Viewing staged operations")
        print(session.get_preview_of_staged_operations())

    else:
        print(f"Unrecognized command. Use -h or --help to see list of commands. Use <command> -h to see help specific "
              f"to the command.")


def parse_args(args):

    usage_help = 'usage message for CLI'
    parser = ArgumentParser(
        prog='Video Manager',
        usage=usage_help,
        formatter_class=HelpFormatter,
        add_help=True
    )

    # TODO: write help strings
    filter_help = "write help string for filter_help"
    export_path_help = "write help string for export_path_help"
    profile_path_help = "write help string for profile_path_help"

    subparsers = parser.add_subparsers(dest='command')

    # Clear
    clear_help = "clear all staged operations from command buffer"
    clear_parser = subparsers.add_parser('clear', help=clear_help)

    # Commit
    commit_help = "execute staged operations"
    commit_parser = subparsers.add_parser('commit', help=commit_help)

    # Export
    export_help = "export collection metadata as a json file"
    export_parser = subparsers.add_parser('export', help=export_help)
    export_parser.add_argument(
        'path',
        help=export_path_help,
        metavar='<PATH>')

    # Fetch
    fetch_help = "stage files in collection to be updated with metadata fetched using the specified plugin"
    fetch_parser = subparsers.add_parser('fetch', help=fetch_help)
    fetch_plugins_help = "name of plugin used to fetch data. can be invoked multiple times"
    fetch_plugins = ['GuessitAPI']
    fetch_parser.add_argument(
        'plugins',
        help=fetch_plugins_help,
        choices=fetch_plugins,
        metavar='<PLUGIN>',
        # nargs='+'
    )
    fetch_parser.add_argument(
        '-f', '--filter',
        dest='filters',
        help=filter_help,
        metavar='<FILTER EXPRESSION>',
        action='append',
        default=None
    )

    # Organize
    organize_help = "stage files in collection to be moved to a subdirectory in 'dest'"
    organize_dest_path_help = "write a help string for organize_dest_path_help"
    organize_parser = subparsers.add_parser(
        'organize',
        help=organize_help)
    organize_parser.add_argument(
        'destination_folder',
        help=organize_dest_path_help,
        metavar='<PATH>',
        default=None
    )
    format_str_help = 'format string for generating directory names'
    organize_parser.add_argument(
        '-d', '--dirname',
        dest='dir_name_format',
        help=format_str_help,
        metavar='<FORMAT STRING>',
        default=None
    )
    organize_parser.add_argument(
        '-f', '--filter',
        dest='filters',
        help=filter_help,
        metavar='<FILTER EXPRESSION>',
        action='append',
        default=None
    )

    # Profile
    profile_help = "switch to another profile"
    profile_parser = subparsers.add_parser('profile', help=profile_help)
    profile_parser.add_argument(
        'path',
        help=profile_path_help,
        metavar='<PATH>')

    # Scan
    scan_help = "scan source directory for video files and adds them to the collection"
    scan_parser = subparsers.add_parser('scan', help=scan_help)
    scan_path_help = "path to directory containing files to scan"
    scan_parser.add_argument(
        'path',
        metavar='<PATH>',
        help=scan_path_help
    )

    # Undo
    undo_help = "undo last commit"
    undo_parser = subparsers.add_parser(
        'undo',
        help=undo_help)

    # View
    view_help = "view currently staged operations"
    view_parser = subparsers.add_parser(
        'view',
        help=view_help)

    return parser.parse_args(args)


def run(args: list[str], session: Facade):
    parsed_args = parse_args(args)
    handle_parsed_args(parsed_args, session)
