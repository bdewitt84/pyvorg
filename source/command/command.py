# source/command.py

"""
    Command base class and derived classes providing functions for use
    in the command buffer via the collection class, which include moving
    videos and creating directories.
"""

# Standard library
import logging
import os

# Local imports
from utils.helper import make_dir, move_file


class Command:
    def validate_exec(self):
        raise NotImplementedError

    def validate_undo(self):
        raise NotImplementedError

    def exec(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


