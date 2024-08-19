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


class Command:
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        raise NotImplementedError

    @staticmethod
    def from_dict(d):
        raise NotImplementedError

    @staticmethod
    def from_json(j):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    def validate_exec(self):
        raise NotImplementedError

    def validate_undo(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError



