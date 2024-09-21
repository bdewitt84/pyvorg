# ./source/tests/test_service/test_cmd_svc.py

"""
    Unit tests for cmd_svc.py
"""

# Standard library
from unittest import TestCase
from unittest.mock import call, patch, MagicMock, Mock

# Local imports
import source.service.cmd_svc as cmd_svc
from source.state.combuffer import CommandBuffer
from source.state.command import Command
from source.commands.movevideo_cmd import MoveVideo
from source.commands.updatemetadata_cmd import UpdateVideoData

# Third-party packages
# n/a


class TestCmdSvc(TestCase):
    def setUp(self) -> None:
        self.command_buffer = CommandBuffer()

    def tearDown(self) -> None:
        pass

    def test_clear_exec_buffer(self):
        # Arrange
        mock_cmd_1 = Mock()
        mock_cmd_2 = Mock()
        self.command_buffer.cmd_buffer.append(mock_cmd_1)
        self.command_buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        cmd_svc.clear_exec_buffer(self.command_buffer)

        # Assert
        self.assertEqual(0, len(self.command_buffer.cmd_buffer))

    def test_execute_cmd_buffer(self):
        # Arrange
        cmd1 = Mock()
        cmd2 = Mock()
        self.command_buffer.cmd_buffer.append(cmd1)
        self.command_buffer.cmd_buffer.append(cmd2)

        # Act
        cmd_svc.execute_cmd_buffer(self.command_buffer)

        # Assert
        self.assertFalse(self.command_buffer.cmd_buffer)
        cmd1.exec.assert_called_once()
        cmd2.exec.assert_called_once()
        self.assertTrue(self.command_buffer.undo_buffer == [cmd1, cmd2])

    def test_get_exec_preview(self):
        # Arrange
        mock_cmd_1 = MagicMock()
        mock_cmd_2 = MagicMock()

        mock_cmd_1.__str__ = lambda x: 'mock 1\n'
        mock_cmd_2.__str__ = lambda x: 'mock 2\n'

        self.command_buffer.cmd_buffer.append(mock_cmd_1)
        self.command_buffer.cmd_buffer.append(mock_cmd_2)

        # Act
        # result = self.command_buffer.preview_buffer()
        result = cmd_svc.get_exec_preview(self.command_buffer)

        # Assert
        self.assertIn('mock 1', result)
        self.assertIn('mock 2', result)

    @patch('source.service.cmd_svc.get_command_from_name')
    def test_build_command(self, mock_get_command_from_name):
        # Arrange
        mock_cmd = Mock()
        mock_get_command_from_name.return_value = mock_cmd
        args = ('arg_1', 'arg_2')
        kwargs = {'test_key': 'test_val'}

        # Act
        cmd_svc.build_command('any_cmd', *args, **kwargs)

        # Assert
        mock_cmd.assert_called_with('arg_1', 'arg_2', test_key='test_val')

    @patch('source.service.cmd_svc.get_command_from_name')
    def test_build_commands(self, mock_get_command_from_name):
        # Arrange
        mock_cmd = Mock()
        mock_get_command_from_name.return_value = mock_cmd

        cmd_args_tuples = [
            ('arg_1_1', 'arg_1_2'),
            ('arg_2_1', 'arg_2_2')
        ]

        cmd_kwargs_dicts = [
            {'kw_1_1': 'val_1_1'},
            {'kw_2_1': 'val_2_1'}
        ]

        # Act
        cmd_svc.build_commands('any_cmd', cmd_args_tuples, cmd_kwargs_dicts)

        # Assert
        mock_cmd.assert_has_calls(
            [
                call('arg_1_1', 'arg_1_2', kw_1_1='val_1_1'),
                call('arg_2_1', 'arg_2_2', kw_2_1='val_2_1')
            ]
        )

    def test_get_command_from_name(self):
        # Arrange
        # Act
        result_move_video = cmd_svc.get_command_from_name('MoveVideo')
        result_update_video_data = cmd_svc.get_command_from_name('UpdateVideoData')

        # Assert
        self.assertEqual(result_move_video, MoveVideo)
        self.assertEqual(result_update_video_data, UpdateVideoData)

    def test_stage_commands(self):
        # Arrange
        class MockCmd(Command):
            pass

        cmd_1 = MockCmd()
        cmd_2 = MockCmd()
        cmds = [cmd_1, cmd_2]

        # Act
        cmd_svc.stage_commands(self.command_buffer, cmds)

        # Assert
        self.assertIn(cmd_1, self.command_buffer.cmd_buffer)
        self.assertIn(cmd_2, self.command_buffer.cmd_buffer)

    def test_execute_undo_buffer(self):
        # Arrange
        cmd1 = Mock()
        cmd2 = Mock()
        self.command_buffer.undo_buffer.append(cmd1)
        self.command_buffer.undo_buffer.append(cmd2)

        # Act
        cmd_svc.execute_undo_buffer(self.command_buffer)

        # Assert
        self.assertFalse(self.command_buffer.undo_buffer)
        cmd1.undo.assert_called_once()
        cmd2.undo.assert_called_once()
