# tests/test_combuffer.py

"""
    Unit tests for source/command/combuffer.py
"""

# Standard library
import unittest
from unittest.mock import Mock

# Local imports
from state.combuffer import *
from test_state.shared import FauxCmd


class TestCommandBuffer(unittest.TestCase):
    def setUp(self) -> None:
        self.buffer = CommandBuffer()

    def tearDown(self) -> None:
        pass

    def test_add_command_valid(self):
        cmd = FauxCmd()
        self.buffer.add_command(cmd)
        self.assertTrue(cmd in self.buffer.cmd_buffer)

    def test_add_command_invalid(self):
        cmd = False
        with self.assertRaises(ValueError):
            self.buffer.add_command(cmd)  # type:ignore

    def test_clear_exec_buffer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_clear_undo_buffer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_execute_cmd_buffer(self):
        cmd1 = FauxCmd()
        cmd2 = FauxCmd()
        cmd3 = FauxCmd()
        self.buffer.cmd_buffer.append(cmd1)
        self.buffer.cmd_buffer.append(cmd2)
        self.buffer.cmd_buffer.append(cmd3)

        self.buffer.execute_cmd_buffer()
        self.assertFalse(self.buffer.cmd_buffer)
        self.assertTrue(cmd1.execute_called)
        self.assertTrue(cmd2.execute_called)
        self.assertTrue(cmd3.execute_called)
        self.assertTrue(self.buffer.undo_buffer == [cmd1, cmd2, cmd3])

    def test_exec_command(self):
        cmd = FauxCmd()
        self.buffer.cmd_buffer.append(cmd)

        self.buffer.exec_command()
        self.assertTrue(cmd.execute_called)
        self.assertFalse(self.buffer.cmd_buffer)
        self.assertTrue(cmd in self.buffer.undo_buffer)

    def test_execute_undo_buffer(self):
        # Arrange
        cmd1 = FauxCmd()
        cmd2 = FauxCmd()
        cmd3 = FauxCmd()
        self.buffer.undo_buffer.append(cmd1)
        self.buffer.undo_buffer.append(cmd2)
        self.buffer.undo_buffer.append(cmd3)

        # Act
        self.buffer.execute_undo_buffer()

        # Assert
        self.assertFalse(self.buffer.undo_buffer)
        self.assertTrue(cmd1.undo_called)
        self.assertTrue(cmd2.undo_called)
        self.assertTrue(cmd3.undo_called)

    def test_from_dict(self):
        # TODO: Implement in source
        pass

    def test_from_json(self):
        # TODO: Implement in source
        pass


    def test_preview_buffer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_undo_cmd(self):
        cmd = FauxCmd()
        self.buffer.undo_buffer.append(cmd)

        self.buffer.undo_cmd()
        self.assertTrue(cmd.undo_called)
        self.assertFalse(self.buffer.undo_buffer)

    def test_validate_exec_buffer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_validate_undo_buffer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_to_dict(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_to_json(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test__str__(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass
