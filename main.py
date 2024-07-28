# Standard Python imports
import sys

# Local imports
from source.cli.ui import parse_args, handle_parsed_args

# Third-party packages


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    handle_parsed_args(args)
