# source/command_base.py

"""
    Command base class and derived classes providing functions for use
    in the command buffer via the collection class, which include moving
    videos and creating directories.
"""

# Standard library
from abc import ABC

# Local imports
# n/a

# Third-party packages
# n/a


class Command(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def validate_exec(self):
        raise NotImplementedError

    def validate_undo(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError
