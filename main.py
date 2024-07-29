# Standard Python imports
import sys

# Local imports
from source.cli.ui import parse_args, handle_parsed_args
from source.session.session_man import SessionManager

# Third-party packages


if __name__ == "__main__":
    session = SessionManager.unpickle_session()
    args = parse_args(sys.argv[1:])
    handle_parsed_args(args, session)
    session.pickle_session()
