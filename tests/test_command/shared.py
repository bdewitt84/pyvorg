# ./tests/test_command/shared.py

"""
Resources shared by tests/test_command unit test package
"""

# Standard library

# Local imports
from source.command.command import Command

# Third-party packages


class TestCommand(Command):

    def __init__(self):
        self.exec_is_valid_called = False
        self.undo_is_valid_called = False
        self.execute_called = False
        self.undo_called = False

    def exec(self):
        self.execute_called = True

    @staticmethod
    def from_dict(d):
        pass

    @staticmethod
    def from_json(j):
        pass

    def to_dict(self):
        pass

    def to_json(self):
        pass

    def undo(self):
        self.undo_called = True

    def validate_exec(self):
        self.exec_is_valid_called = True

    def validate_undo(self):
        self.undo_is_valid_called = True
