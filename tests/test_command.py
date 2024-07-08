# tests/test_command.py

"""
Unit tests for source/command.py
"""

# Standard library
import tempfile
import unittest

# Local imports
from source.command import *
from source.video import Video


class TestMoveVideoCommand(unittest.TestCase):

    def setUp(self) -> None:
        # Set up temp directory structure
        self.src_dir = tempfile.TemporaryDirectory()
        self.dest_dir = os.path.join(self.src_dir.name, 'dest\\')
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

    def setup_undo(self):
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

    def tearDown(self) -> None:
        self.src_dir.cleanup()

    def test_exec(self):
        expected_path = os.path.join(self.dest_dir, self.filename)
        self.cmd.execute()
        actual_path = self.vid.get_path()
        self.assertTrue(os.path.exists(actual_path))
        self.assertEqual(expected_path, actual_path)

    def test_undo(self):
        expected_file_path = self.src_file_path
        self.setup_undo()
        self.cmd.undo()
        self.assertTrue(os.path.exists(expected_file_path))
        self.assertEqual(expected_file_path, self.vid.get_path())
        self.assertFalse(os.path.exists(self.dest_dir))
