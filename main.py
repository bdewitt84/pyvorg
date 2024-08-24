# Standard Python imports
import sys

# Local imports
from source.ui.cli import run
from source.facade.facade import Facade

# Third-party packages


if __name__ == "__main__":
    session = Facade()
    run(sys.argv[1:], session)
