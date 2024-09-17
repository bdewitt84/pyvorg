# tests/test_command/test_move_video.py

"""
    Unit tests for source/command/move_video.py
"""

# Standard library
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

# Local imports
from source.state.move_video import MoveVideo
from source.state.video import Video

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
        self.vid = Video(self.src_file_path)

        # Create MoveCommand object
        self.test_cmd = MoveVideo(self.vid, self.dest_dir)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_exec(self):
        # Arrange
        expected_dest_file = self.dest_dir / self.filename

        # Act
        self.test_cmd.exec()

        # Assert
        self.assertEqual(self.test_cmd.origin_dir, self.src_dir)
        self.assertTrue(expected_dest_file.exists())

    def test_to_dict(self):
        # Arrange
        self.test_cmd.dest_dir = Path('dest_dir')
        self.test_cmd.origin_dir = Path('origin_dir')
        self.test_cmd.created_dirs = [
            Path('created_dir_1'),
            Path('created_dir_2')
        ]
        self.test_cmd.video = Mock()
        self.test_cmd.video.to_dict.return_value = {'vid_key': 'vid_val'}

        # Act
        result = self.test_cmd.to_dict()

        # Assert
        self.assertIsInstance(result.get('video'), dict)
        self.assertEqual(result.get('video').get('vid_key'), 'vid_val')
        self.assertEqual(result.get('dest_dir'), Path('dest_dir'))
        self.assertEqual(result.get('origin_dir'), Path('origin_dir'))
        self.assertEqual(result.get('created_dirs'), [
            Path('created_dir_1'),
            Path('created_dir_2')
        ])

    def test_undo(self):
        # Arrange
        self.test_cmd.exec()

        # Act
        self.test_cmd.undo()

        # Assert
        self.assertTrue(self.src_file_path.exists())
        self.assertFalse((self.dest_dir / self.filename).exists())

    @patch('source.state.move_video.file_svc.validate_move')
    def test_validate_exec(self, mock_validate_move):
        # Arrange
        self.test_cmd.video = Mock()
        self.test_cmd.video.get_filename.return_value = 'video.file'
        self.test_cmd.video.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.dest_dir = Path('target dir')

        # Act
        self.test_cmd.validate_exec()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('target dir') / 'video.file'
        mock_validate_move.assert_called_once_with(src_path, dest_path)

    @patch('source.service.file_svc.validate_move')
    def test_validate_undo(self, mock_validate_move):
        # Arrange
        self.test_cmd.video = Mock()
        self.test_cmd.video.get_filename.return_value = 'video.file'
        self.test_cmd.video.get_path.return_value = Path('current dir') / 'video.file'
        self.test_cmd.origin_dir = 'original dir'

        # Act
        self.test_cmd.validate_undo()

        # Assert
        src_path = Path('current dir') / 'video.file'
        dest_path = Path('original dir') / 'video.file'
        mock_validate_move.assert_called_with(src_path, dest_path)
