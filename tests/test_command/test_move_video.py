# tests/test_command/test_move_video.py

"""
    Unit tests for source/command/move_video.py
"""

# Standard library
import shutil
import tempfile
import unittest
from unittest.mock import patch

# Local imports
from source.constants import *
from source.command.move_video import *
from collection.video import Video

# Third-party packages


class TestMoveVideoCommand(unittest.TestCase):

    def setUp(self) -> None:
        # Set up temp directory structure
        self.src_dir = tempfile.TemporaryDirectory()
        self.dest_dir = os.path.join(self.src_dir.name, 'dest')
        os.makedirs(self.dest_dir)

        # Create temp video file
        self.filename = 'tempfile.mp4'
        self.src_file_path = os.path.join(self.src_dir.name, self.filename)
        self.test_file = open(self.src_file_path, 'w')
        self.test_file.close()

        # Create temp video object
        self.vid = Video()
        self.vid.data = {
            "file_data": {
                "path": self.src_file_path,
                "root": self.src_dir.name,
                "filename": self.filename
            }
        }

        # Create MoveCommand object
        self.cmd = MoveVideo(self.vid, self.dest_dir)

    def tearDown(self) -> None:
        self.src_dir.cleanup()

    def test_exec(self):
        expected_path = os.path.join(self.dest_dir, self.filename)
        self.cmd.exec()
        actual_path = self.vid.get_path()
        self.assertTrue(os.path.exists(actual_path))
        self.assertEqual(expected_path, actual_path)

    def setUp_undo(self):
        self.cmd.undo_dir = self.src_dir.name
        self.cmd.created_dirs.append(self.dest_dir)
        self.moved_path = shutil.move(self.test_file.name, self.dest_dir)
        self.vid.data = {
            "file_data": {
                "path": self.moved_path,
                "root": self.dest_dir,
                "filename": self.filename
            }
        }

    def test_undo(self):
        expected_file_path = self.src_file_path
        self.setUp_undo()
        self.cmd.undo()
        self.assertTrue(os.path.exists(expected_file_path))
        self.assertEqual(expected_file_path, self.vid.get_path())
        self.assertFalse(os.path.exists(self.dest_dir))

    def test_validate_exec_true(self):
        valid, _ = self.cmd.validate_exec()
        self.assertTrue(valid)

    def test_validate_exec_src_does_not_exist(self):
        self.vid.data[FILE_DATA].update(
            {"path": os.path.join(self.src_dir.name, 'does_not_exist.file')}
        )
        valid, msg = self.cmd.validate_exec()
        print(msg)
        self.assertFalse(valid)

    def test_validate_exec_dst_already_exists(self):
        exists_file = os.path.join(self.dest_dir, self.vid.data[FILE_DATA][FILENAME])
        with open(exists_file, 'w'):
            valid, msg = self.cmd.validate_exec()
            print(msg)
        self.assertFalse(valid)

    @patch('os.access')
    def test_validate_exec_src_no_read(self, mock_access):
        mock_access.side_effect = lambda path, mode: mode != os.R_OK
        valid, msg = self.cmd.validate_exec()
        print(msg)
        self.assertFalse(valid, "Source file should not have read permission")
        self.assertTrue(any('read' in m for m in msg), "'read' does not appear in the error message")

    @patch('os.access')
    def test_validate_exec_src_no_write(self, mock_access):
        mock_access.side_effect = lambda path, mode: False if (path == self.src_file_path and mode == os.W_OK) else True
        valid, msg = self.cmd.validate_exec()
        print(msg)
        self.assertFalse(valid, "Source file should not have write permission")
        self.assertTrue(any('write' in m for m in msg))

    @patch('os.access')
    def test_validate_exec_dst_no_write(self, mock_access):
        mock_access.side_effect = lambda path, mode: False if (path == self.dest_dir and mode == os.W_OK) else True
        print('test: ' + self.dest_dir)
        valid, msg = self.cmd.validate_exec()
        print(msg)
        self.assertFalse(valid, "Destination file should not have write permission")
        self.assertTrue(any('write' in m for m in msg))

    def test_validate_undo_true(self):
        self.setUp_undo()
        valid, _ = self.cmd.validate_undo()
        self.assertTrue(valid)

    def test_validate_undo_does_not_exist(self):
        self.setUp_undo()
        self.vid.data[FILE_DATA].update(
            {"path": os.path.join(self.src_dir.name, 'does_not_exist.file')}
        )
        valid, msg = self.cmd.validate_undo()
        self.assertFalse(valid)
        self.assertTrue(any('does not exist' in m for m in msg))

    def test_validate_undo_already_exists(self):
        self.setUp_undo()
        with open(self.src_file_path, 'w'):
            valid, msg = self.cmd.validate_undo()
            print(msg)
            self.assertFalse(valid)
            self.assertTrue(any('already exists' in m for m in msg))

    @patch('os.access')
    def test_validate_undo_src_no_read(self, mock_access):
        self.setUp_undo()
        mock_access.side_effect = lambda path, mode: False if (path == self.moved_path and mode == os.R_OK) else True
        valid, msg = self.cmd.validate_undo()
        print(msg)
        self.assertFalse(valid)
        self.assertTrue(any('read' in m for m in msg))

    @patch('os.access')
    def test_validate_undo_src_no_write(self, mock_access):
        self.setUp_undo()
        mock_access.side_effect = lambda path, mode: False if (path == self.moved_path and mode == os.W_OK) else True
        valid, msg = self.cmd.validate_undo()
        print(msg)
        self.assertFalse(valid)
        self.assertTrue(any('write' in m for m in msg))

    @patch('os.access')
    def test_validate_undo_dst_no_write(self, mock_access):
        self.setUp_undo()
        mock_access.side_effect = lambda path, mode: False if (path == self.src_dir.name and mode == os.W_OK) else True
        print(self.src_dir.name)
        valid, msg = self.cmd.validate_undo()
        print(msg)
        self.assertFalse(valid)
        self.assertTrue(any('write' in m for m in msg))
