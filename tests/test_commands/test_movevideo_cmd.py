# tests/test_command/test_movevideo_cmd.py

"""
    Unit tests for source/command/movevideo_cmd.py
"""

# Standard library
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

# Local imports
from source.commands.movevideo_cmd import MoveVideoCmd
from source.state.mediafile import MediaFile
from source.utils import fileutils


# Third-party packages
# n/a


class TestMoveVideoCommand(unittest.TestCase):

    def setUp(self) -> None:
        # Set up temp directory structure
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = Path(self.temp_dir.name)
        self.dest_dir = Path(self.src_dir) / 'dest'

        # Create temp video file
        self.filename = 'tempfile.mp4'
        self.src_file_path = Path(self.temp_dir.name) / self.filename
        with self.src_file_path.open('w') as file:
            file.write('dummy data')
            assert self.src_file_path.exists()

        # Create temp video object
        self.vid = MediaFile(self.src_file_path)

        # Create MoveCommand object
        self.test_cmd = MoveVideoCmd(self.vid, self.dest_dir, 'format_str')

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_exec(self):
        # Arrange
        expected_dest_file = self.dest_dir / 'format_str' / self.filename

        # Act
        self.test_cmd.exec()

        # Assert
        self.assertEqual(self.test_cmd.origin_dir, self.src_dir)
        self.assertTrue(expected_dest_file.exists())

    def test_undo(self):
        # Arrange
        self.test_cmd.exec()

        # Act
        self.test_cmd.undo()

        # Assert
        self.assertTrue(self.src_file_path.exists())
        self.assertFalse((self.dest_dir / self.filename).exists())

    def test_update_origin_dir(self):
        # Arrange
        self.test_cmd.origin_dir = None

        # Act
        self.test_cmd._update_origin_dir()

        # Assert
        expected = self.vid.get_root()
        self.assertEqual(expected, self.test_cmd.origin_dir)

    def test_update_target_file_path(self):
        # Arrange

        # Act
        self.test_cmd._update_target_file_path()

        # Assert
        expected = self.dest_dir / 'format_str' / self.vid.get_filename()
        self.assertEqual(expected, self.test_cmd.target_file_path)

    @patch.object(fileutils, 'make_dirs')
    def test_make_dirs(self, mock_make_dirs):
        # Arrange
        # Act
        # Assert
        mock_make_dirs.called_once_with(self.test_cmd.target_subdir)

    def test_move_video(self):
        # Arrange
        self.dest_dir.mkdir()
        self.test_cmd.target_subdir = self.dest_dir / 'format_str'
        self.test_cmd.target_subdir.mkdir()

        # Act
        self.test_cmd._move_video()

        # Assert
        expected_dest_file = self.dest_dir / 'format_str' / self.filename
        self.assertTrue(expected_dest_file.exists())

    @patch.object(fileutils, 'validate_move')
    def test_validate_exec(self, mock_validate_move):
        # Arrange
        self.test_cmd.video = Mock()
        self.test_cmd.video.get_filename.return_value = 'video.file'
        self.test_cmd.video.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.target_root = Path('target dir')

        # Act
        self.test_cmd.validate_exec()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('target dir') / 'format_str' / 'video.file'
        mock_validate_move.assert_called_once_with(src_path, dest_path)

    @patch.object(fileutils, 'validate_move')
    def test_validate_undo(self, mock_validate_move):
        # Arrange
        self.test_cmd.video = Mock()
        self.test_cmd.video.get_filename.return_value = 'video.file'
        self.test_cmd.video.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.origin_dir = Path('original dir')

        # Act
        self.test_cmd.validate_undo()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('original dir') / 'video.file'
        mock_validate_move.assert_called_with(src_path, dest_path)
