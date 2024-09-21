# tests/test_command.py

"""
    Unit tests for source/state/command_base.py
"""

# Standard library
from unittest import TestCase

# Local imports
from source.commands.cmdbuffer import *


class TestCommand(TestCase):
    def setUp(self) -> None:
        class SubClass(Command):
            def exec(self):
                super().exec()

            def to_dict(self):
                super().to_dict()

            def validate_exec(self):
                super().validate_exec()

            def validate_undo(self):
                super().validate_undo()

            def undo(self):
                super().undo()

        self.SubClass = SubClass
        self.subclass = SubClass()

    def tearDown(self) -> None:
        pass

    def test_exec(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.exec()

    def test_to_dict(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.to_dict()

    def test_validate_exec(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.exec()

    def test_validate_undo(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.validate_undo()

    def test_undo(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.undo()
