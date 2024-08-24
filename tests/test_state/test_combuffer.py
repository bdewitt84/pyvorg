# tests/test_combuffer.py

"""
    Unit tests for source/command/combuffer.py
"""

# Standard library
import unittest
from unittest.mock import Mock

# Local imports
from state.combuffer import *
from test_state.shared import TestCommand


class TestCommandBuffer(unittest.TestCase):
    def setUp(self) -> None:
        self.buffer = CommandBuffer()

    def test_stage_command_valid(self):
        cmd = TestCommand()
        self.buffer.add_command(cmd)
        self.assertTrue(cmd in self.buffer.cmd_buffer)

    def test_stage_command_invalid(self):
        cmd = False
        with self.assertRaises(ValueError):
            self.buffer.add_command(cmd)  # type:ignore

    def test_exec_command(self):
        cmd = TestCommand()
        self.buffer.cmd_buffer.append(cmd)

        self.buffer.exec_command()
        self.assertTrue(cmd.execute_called)
        self.assertFalse(self.buffer.cmd_buffer)
        self.assertTrue(cmd in self.buffer.undo_buffer)

    def test_undo_cmd(self):
        cmd = TestCommand()
        self.buffer.undo_buffer.append(cmd)

        self.buffer.undo_cmd()
        self.assertTrue(cmd.undo_called)
        self.assertFalse(self.buffer.undo_buffer)

    def test_execute_buffer(self):
        cmd1 = TestCommand()
        cmd2 = TestCommand()
        cmd3 = TestCommand()
        self.buffer.cmd_buffer.append(cmd1)
        self.buffer.cmd_buffer.append(cmd2)
        self.buffer.cmd_buffer.append(cmd3)

        self.buffer.execute_cmd_buffer()
        self.assertFalse(self.buffer.cmd_buffer)
        self.assertTrue(cmd1.execute_called)
        self.assertTrue(cmd2.execute_called)
        self.assertTrue(cmd3.execute_called)
        self.assertTrue(self.buffer.undo_buffer == [cmd1, cmd2, cmd3])

    def test_execute_undo_buffer(self):
        # Arrange
        cmd1 = TestCommand()
        cmd2 = TestCommand()
        cmd3 = TestCommand()
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

    def preview_buffer(self):
        pass

    def save_buffer(self):
        vid = Mock()
        cmd = Mock()
        cmd.video = vid
        cmd.str = 'string'
        cmd.int = 1
        self.buffer.cmd_buffer.put(cmd)

    def load_buffer(self):
        pass
