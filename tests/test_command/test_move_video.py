# tests/test_command/test_move_video.py

"""
    Unit tests for source/command/move_video.py
"""

# Standard library
from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, Mock, patch

# Local imports
from source.command.move_video import MoveVideo

# Third-party packages


class TestMoveVideoCommand(unittest.TestCase):

    def setUp(self) -> None:
        # Set up temp directory structure
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = Path(self.temp_dir.name)
        self.dest_dir = Path(self.src_dir) / 'dest'
        self.dest_dir.mkdir()

        # Create temp video file
        self.filename = 'tempfile.mp4'
        self.src_file_path = Path(self.temp_dir.name) / self.filename
        with self.src_file_path.open('w') as file:
            file.write('dummy data')

        # Create temp video object
        self.vid = Mock()
        self.vid.data = {
            "file_data": {
                "path": self.src_file_path,
                "root": self.temp_dir.name,
                "filename": self.filename
            }
        }
        self.vid.get_filename.return_value = self.filename
        self.vid.get_path.return_value = self.src_dir / self.filename
        self.vid.get_root.return_value = self.src_dir

        # Create MoveCommand object
        self.test_cmd = MoveVideo(self.vid, self.dest_dir)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @patch('source.command.move_video.MoveVideo._move')
    def test_exec(self, mock_move):
        # Act
        self.test_cmd.exec()

        # Assert
        self.assertEqual(self.test_cmd.origin_dir, self.src_dir)
        mock_move.assert_called_once_with(self.dest_dir)

    @patch('source.command.move_video.move_file')
    @patch('source.command.move_video.MoveVideo._make_dirs')
    def test_move(self, mock_make_dirs, mock_move_file):
        # Arrange
        dest_path = self.dest_dir / self.filename

        # Act
        self.test_cmd._move(self.dest_dir)

        # Assert
        mock_make_dirs.assert_called_once_with(self.dest_dir)
        mock_move_file.assert_called_once_with(self.vid.get_path(), dest_path)
        self.vid.update_file_data.assert_called_once_with(dest_path)

    @patch('source.command.move_video.MoveVideo._undo_make_dirs')
    @patch('source.command.move_video.MoveVideo._move')
    def test_undo(self, mock_move, mock_undo_make_dirs):
        # Arrange
        self.test_cmd.origin_dir = 'fake_path'

        # Act
        self.test_cmd.undo()

        # Assert
        mock_move.assert_called_once_with('fake_path')
        mock_undo_make_dirs.assert_called_once()

    @patch('source.command.move_video.dir_is_empty')
    def test_undo_make_dirs(self, mock_dir_is_empty):
        # Arrange
        empty_dir = Mock()
        not_empty_dir = Mock()
        doesnt_exist_dir = Mock()

        empty_dir.exists.return_value = True
        not_empty_dir.exists.return_value = True
        doesnt_exist_dir.exists.return_value = True

        empty_dir.empty = True
        not_empty_dir.empty = False

        mock_dir_is_empty.side_effect = lambda x: True if x.empty else False

        self.test_cmd.created_dirs = [empty_dir, not_empty_dir, doesnt_exist_dir]

        # Act
        self.test_cmd._undo_make_dirs()

        # Assert
        empty_dir.rmdir.assert_called_once()
        not_empty_dir.rmdir.assert_not_called()
        doesnt_exist_dir.remdir.assert_not_called()

    @patch('source.command.move_video.MoveVideo._validate_move')
    def test_validate_exec(self, mock_validate_move):
        # Arrange
        self.vid.get_filename.return_value = 'video.file'
        self.vid.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.dest_dir = Path('target dir')

        # Act
        self.test_cmd.validate_exec()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('target dir') / 'video.file'
        mock_validate_move.assert_called_once_with(src_path, dest_path)

    @patch('source.command.move_video.MoveVideo._validate_move')
    def test_validate_undo(self, mock_validate_move):
        # Arrange
        self.vid.get_filename.return_value = 'video.file'
        self.vid.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.origin_dir = 'original dir'

        # Act
        self.test_cmd.validate_undo()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('original dir') / 'video.file'
        mock_validate_move.assert_called_with(src_path, dest_path)

    @patch('source.command.move_video.path_is_readable')
    @patch('source.command.move_video.path_is_writable')
    def test_validate_move(self, mock_path_is_writable, mock_path_is_readable):
        # Notes: Mocks return True by default when used as a condition in an
        #        if statement. This unit test doesn't test the false branch
        #        of these statements since they only append strings to a list

        # Arrange
        src_path = Mock()
        dest_dir = Mock()
        dest_path = Mock()
        dest_path.parent = dest_dir

        # Act
        result_valid, result_msg = self.test_cmd._validate_move(src_path, dest_path)

        # Assert
        src_path.exists.assert_called_once()
        dest_path.exists.assert_called_once()
        mock_path_is_readable.assert_called_once_with(src_path)
        expected_calls_writable = [call(src_path), call(dest_dir)]
        mock_path_is_writable.assert_has_calls(expected_calls_writable, any_order=True)

        self.assertTrue(result_valid)
        self.assertEqual(result_msg, [])
