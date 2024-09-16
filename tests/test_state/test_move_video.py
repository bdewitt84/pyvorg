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

    @patch('source.state.move_video.MoveVideo._validate_move')
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

    @patch('source.state.move_video.MoveVideo._validate_move')
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

    def test_make_dirs(self):
        # Arrange
        root_path = Path(self.temp_dir.name)
        l1_path = root_path / 'lvl1'
        l2_path = l1_path / 'lvl2'
        l3_path = l2_path / 'lvl3'

        # Act
        self.test_cmd._make_dirs([l3_path, l2_path, l1_path])

        # Assert
        self.assertTrue(l1_path.exists())
        self.assertTrue(l2_path.exists())
        self.assertTrue(l3_path.exists())

    # @patch('source.state.move_video.move_file')
    # def test_move(self, mock_move_file):
    #     # Arrange
    #     dest_path = self.dest_dir / self.filename
    #
    #     # Act
    #     self.test_cmd._move(self.dest_dir)
    #
    #     # Assert
    #     mock_move_file.assert_called_once_with(self.vid.get_path(), dest_path)
    #     self.vid.update_file_data.assert_called_once_with(dest_path, skip_hash=True)

    def test_undo_make_dirs(self):
        # Arrange
        root_path = Path(self.temp_dir.name)
        l1_path = root_path / 'lvl1'
        l2_path = l1_path / 'lvl2'
        l3_path = l2_path / 'lvl3'

        dirs = [l3_path, l2_path, l1_path]

        for directory in reversed(dirs):
            directory.mkdir()
            assert directory.exists()

        # Act
        self.test_cmd._undo_make_dirs(dirs)

        # Assert
        self.assertFalse(l3_path.exists())
        self.assertFalse(l2_path.exists())
        self.assertFalse(l1_path.exists())

    @patch('source.state.move_video.path_is_readable')
    @patch('source.state.move_video.path_is_writable')
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
