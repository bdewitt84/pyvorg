# tests/test_combuffer.py

"""
    Unit tests for source/command/cmdbuffer.py
"""

# Standard library
import unittest
from unittest.mock import MagicMock, Mock

# Local imports
from source.commands.cmdbuffer import *
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
        # Arrange
        mock_cmd_1 = Mock()
        mock_cmd_2 = Mock()
        self.buffer.cmd_buffer.append(mock_cmd_1)
        self.buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        self.buffer.clear_exec_buffer()

        # Assert
        self.assertEqual(0, len(self.buffer.cmd_buffer))

    def test_clear_undo_buffer(self):
        # Arrange
        mock_cmd_1 = Mock()
        mock_cmd_2 = Mock()
        self.buffer.undo_buffer.append(mock_cmd_1)
        self.buffer.undo_buffer.append(mock_cmd_2)

        # Act
        self.buffer.clear_undo_buffer()

        # Assert
        self.assertEqual(0, len(self.buffer.undo_buffer))

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

    def test_preview_buffer(self):
        # Arrange
        mock_cmd_1 = MagicMock()
        mock_cmd_2 = MagicMock()

        mock_cmd_1.__str__ = lambda x: 'mock 1\n'
        mock_cmd_2.__str__ = lambda x: 'mock 2\n'

        self.buffer.cmd_buffer.append(mock_cmd_1)
        self.buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        result = self.buffer.preview_buffer()

        # Assert
        self.assertIn('mock 1', result)
        self.assertIn('mock 2', result)

    def test_undo_cmd(self):
        cmd = FauxCmd()
        self.buffer.undo_buffer.append(cmd)

        self.buffer.undo_cmd()
        self.assertTrue(cmd.undo_called)
        self.assertFalse(self.buffer.undo_buffer)

    def test_validate_exec_buffer(self):
        # Arrange
        mock_cmd_1 = Mock()
        mock_cmd_2 = Mock()

        mock_cmd_1.validate_exec.return_value = (0, 'err msg 1')
        mock_cmd_2.validate_exec.return_value = (0, 'err msg 2')

        self.buffer.cmd_buffer.append(mock_cmd_1)
        self.buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        self.buffer.validate_exec_buffer()

        # Assert
        mock_cmd_1.validate_exec.assert_called_once()
        mock_cmd_2.validate_exec.assert_called_once()

    def test_validate_undo_buffer(self):
        # Arrange
        mock_cmd_1 = Mock()
        mock_cmd_2 = Mock()
        self.buffer.undo_buffer.append(mock_cmd_1)
        self.buffer.undo_buffer.append(mock_cmd_2)

        # Act
        self.buffer.validate_undo_buffer()

        # Assert
        mock_cmd_1.validate_undo.assert_called_once()
        mock_cmd_2.validate_undo.assert_called_once()

    def test_to_dict(self):
        # TODO: Implement in source
        # Arrange
        # Act
        # Assert
        pass

    def test__str__(self):
        # Arrange
        mock_cmd_1 = MagicMock()
        mock_cmd_2 = MagicMock()

        mock_cmd_1.__str__ = lambda x: 'mock 1\n'
        mock_cmd_2.__str__ = lambda x: 'mock 2\n'

        self.buffer.cmd_buffer.append(mock_cmd_1)
        self.buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        result = str(self.buffer)

        # Assert
        self.assertIn('mock 1', result)
        self.assertIn('mock 2', result)
