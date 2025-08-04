# ./main.py

# Standard Python imports
import sys

# Local imports
from source.state.col import Collection
from source.commands.cmdbuffer import CommandBuffer
from source.facade.pyvorg_facade import Facade
from source.ui.cli import run

# Third-party packages


def main():
    session = Facade()
    run(sys.argv[1:], session)
