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
        pre_undo_path = os.path.join(self.dest_dir, self.filename)
        self.moved_path = shutil.move(self.test_file.name, pre_undo_path)
        self.vid.data = {
            "file_data": {
                "path": pre_undo_path,
                "root": self.dest_dir,
                "filename": self.filename
            }
        }

    def tearDown(self) -> None:
        self.src_dir.cleanup()

    def test_validate_exec_valid(self):
        self.cmd.validate_exec()

    def test_validate_exec_invalid_src(self):
        os.remove(self.test_file.name)
        cmd = MoveVideo(self.vid, self.dest_dir)
        with self.assertRaises(ValidationError):
            cmd._validate_file_exists(cmd.src_file_path)
        with self.assertRaises(ValidationError):
            cmd.validate_exec()

    def test_validate_exec_dest_already_exists(self):
        dest_file_path = os.path.join(self.dest_dir, self.filename)
        temp_file = open(dest_file_path, 'w')
        temp_file.close()
        with self.assertRaises(ValidationError):
            self.cmd._validate_file_not_exist(self.cmd.dest_file_path)
        with self.assertRaises(ValidationError):
            self.cmd.validate_exec()

    def test_validate_exec_path_has_changed(self):
        dest = os.path.join(self.src_dir.name, 'new_folder')
        os.makedirs(dest)
        new_path = shutil.move(self.test_file.name, dest)
        new_root, new_filename = os.path.split(new_path)

        self.vid.data = {
            "file_data": {
                "path": new_path,
                "root": new_root,
                "filename": new_filename
            }
        }

        with self.assertRaises(ValidationError):
            self.cmd._validate_path_not_changed(self.cmd.src_file_path)
        with self.assertRaises(ValidationError):
            self.cmd.validate_exec()

    def test_validate_undo_valid(self):
        self.setup_undo()
        self.cmd.undo()

    def test_validate_undo_invalid_src(self):
        self.setup_undo()
        os.remove(self.moved_path)
        with self.assertRaises(ValidationError):
            self.cmd._validate_file_exists(self.cmd.dest_file_path)

    def test_validate_undo_dest_already_exists(self):
        self.setup_undo()
        temp_file = open(self.src_file_path, 'w')
        temp_file.close()
        with self.assertRaises(ValidationError):
            self.cmd._validate_file_not_exist(self.cmd.src_file_path)

    def test_validate_undo_path_has_changed(self):
        self.setup_undo()

        dest = os.path.join(self.src_dir.name, 'new_folder')
        os.makedirs(dest)
        new_path = shutil.move(self.moved_path, dest)
        new_root, new_filename = os.path.split(new_path)

        self.vid.data = {
            "file_data": {
                "path": new_path,
                "root": new_root,
                "filename": new_filename
            }
        }

        with self.assertRaises(ValidationError):
            self.cmd._validate_path_not_changed(self.cmd.dest_file_path)

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
