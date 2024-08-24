# Standard Python imports
import sys

# Local imports
from source.ui.cli import run
from source.facade.pyvorg_session import PyvorgSession

# Third-party packages


if __name__ == "__main__":
    session = PyvorgSession()
    run(sys.argv[1:], session)
