# /source/cli/ui.py

"""
    Command line interface application for the video manager
"""

# Standard library
from argparse import ArgumentParser, HelpFormatter

# Local imports
# n/a

# Third-party packages
# n/a


def parse_args(args):

    usage_help = 'usage message for CLI'
    parser = ArgumentParser(
        prog='Video Manager',
        usage=usage_help,
        formatter_class=HelpFormatter,
        add_help=True
    )

    subparcers = parser.add_subparsers(dest='command')

    # Commit
    commit_help = "execute staged operations"
    commit_parser = subparcers.add_parser('commit', help=commit_help)

    # Export
    export_help = "export collection metadata as a json file"
    export_parser = subparcers.add_parser('export', help=export_help)
    export_parser.add_argument('path', metavar='PATH')

    # Fetch
    fetch_help = "stage files in collection to be updated with metadata fetched using the specified plugin"
    fetch_parser = subparcers.add_parser('fetch', help=fetch_help)
    fetch_plugin_help = "name of plugin used to fetch data. can be invoked multiple times"
    fetch_plugins = ['test']
    fetch_parser.add_argument(
        'plugins',
        help=fetch_plugin_help,
        choices=fetch_plugins,
        metavar='PLUGIN',
        nargs='+'
    )

    # Organize
    organize_help = "stage files in collection to be moved to a subdirectory in 'dest'"
    organize_parser = subparcers.add_parser('organize', help=organize_help)

    # Profile
    profile_help = "switch to another profile"
    profile_parser = subparcers.add_parser('profile', help = profile_help)
    profile_parser.add_argument('path', metavar='PATH')

    # Scan
    scan_help = "scan source directory for video files and adds them to the collection"
    scan_parser = subparcers.add_parser('scan', help=scan_help)
    scan_path_help = "path to directory containing files to scan"
    scan_parser.add_argument(
        'path',
        metavar='PATH',
        help=scan_path_help
    )

    # Undo
    undo_help = "undo last commit"
    undo_parser = subparcers.add_parser('undo', help=undo_help)

    # View
    view_help = "view currently staged operations"
    view_parser = subparcers.add_parser('view', help=view_help)

    return parser.parse_args(args)


def handle_parsed_args(args, session):

    if args.command == 'commit':
        print("Committing staged operations")
        session.commit_transaction()

    elif args.command == 'export':
        print(f"Exporting collection data to '{args.path}'")
        session.export_collection_metadata(args.path)

    elif args.command == 'fetch':
        print(f"Staging files for fetching data from {args.plugins}")
        for plugin in args.plugins:
            session.stage_update_api_metadata(plugin)

    elif args.command == 'organize':
        print(f"Staging files for organization at '{args.path}'")
        session.stage_organize_video_files()

    elif args.command == 'profile':
        print(f"Switching profile to {args.name}")
        session.set_profile(args.name)

    elif args.command == 'scan':
        print(f"Scanning '{args.path}'")
        session.scan_path(args.path)

    elif args.command == 'undo':
        print(f"Undoing last commit")
        session.undo_transaction()

    elif args.command == 'view':
        print(f"Viewing staged operations")
        session.preview_transaction()

    else:
        print(f"Unrecognized command. Use -h or --help to see list of commands. Use <command> -h to see help specific "
              f"to the command.")
