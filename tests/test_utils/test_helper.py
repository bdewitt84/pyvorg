# tests/test_helper.py

"""
Unit tests for source/helper.py
"""
# Standard library
from tempfile import TemporaryDirectory
from unittest import TestCase

# Local imports
from utils.helper import *


class TestHelper(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.test_data = 'test data'

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_class_name(self):
        # Arrange
        integer = 1
        string = 'string'
        boolean = True
        none = None

        # Act and Assert
        self.assertEqual('int', class_name(integer))
        self.assertEqual('str', class_name(string))
        self.assertEqual('bool', class_name(boolean))
        self.assertEqual('NoneType', class_name(none))

    def test_hash_sha256(self):
        # Arrange
        filename = 'test.file'
        file_path = Path(self.temp_dir.name) / filename
        with file_path.open('wb') as file:
            file.write(b'test_data')

        # Act
        computed_hash = hash_sha256(file_path)

        # Assert
        expected_hash = 'e7d87b738825c33824cf3fd32b7314161fc8c425129163ff5e7260fc7288da36'
        self.assertEqual(expected_hash, computed_hash)

        with self.assertRaises(FileNotFoundError):
            hash_sha256('bogus_file_name')

    def test_move_file(self):
        # Arrange
        src_exists_path = Path(self.temp_dir.name) / 'exists.file'
        src_does_not_exist_path = Path(self.temp_dir.name) / 'does_not_exist.file'
        with src_exists_path.open('w'):
            pass
        dst_path = Path(self.temp_dir.name) / 'dst_folder'

        # Act
        with self.assertRaises(FileNotFoundError):
            move_file(src_does_not_exist_path, dst_path)

        move_file(src_exists_path, dst_path)

        # Assert
        with self.assertRaises(FileExistsError):
            move_file(src_exists_path, dst_path)

        self.assertFalse(src_exists_path.exists())
        self.assertTrue(dst_path.exists())

    def test_path_is_writable(self):
        # Arrange
        writable_target_path = Path(self.temp_dir.name) / 'writable.file'
        non_writable_target_path = Path(self.temp_dir.name) / 'non_writable.file'

        writable_target_path.touch(222)
        non_writable_target_path.touch(555)

        # Act and Assert
        self.assertTrue(path_is_writable(writable_target_path))
        self.assertFalse(path_is_writable(non_writable_target_path))

    def test_timestamp_validate(self):
        # Arrange
        valid_timestamp = '2000-01-01 01:00:00'
        invalid_timestamp = '01:00:00 2000-01-01'

        # Act and assert
        self.assertTrue(timestamp_validate(valid_timestamp))
        self.assertFalse(timestamp_validate(invalid_timestamp))

    def test_file_write(self):
        # Arrange
        write_ok = Path(self.temp_dir.name) / 'write_okay.file'
        already_exists = Path(self.temp_dir.name) / 'already_exists.file'
        with already_exists.open('w'):
            pass

        # Act and Assert
        file_write(write_ok, self.test_data)
        self.assertTrue(write_ok.exists())
        with open(write_ok, 'r') as file:
            written_data = file.read()
        self.assertEqual(written_data, self.test_data)

        with self.assertRaises(FileExistsError):
            file_write(already_exists, self.test_data)

    def test_file_read(self):
        # Arrange
        file_exists = Path(self.temp_dir.name) / 'exists.file'
        file_does_not_exist = Path(self.temp_dir.name) / 'does_not_exist.file'

        file_exists.write_text(self.test_data)

        # Act and assert
        file_read(file_exists)

        with self.assertRaises(FileNotFoundError):
            file_read(file_does_not_exist)

    def test_mimic_folder(self):
        # Arrange
        temp_dir = Path(self.temp_dir.name)
        src_tree = temp_dir / 'src_tree'
        dst_tree = temp_dir / 'dst_tree'

        make = [
            temp_dir / 'src_tree',
            temp_dir / 'src_tree' / 'root.file',
            temp_dir / 'src_tree' / 'sub_dir_1',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub.file',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub_sub_dir',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub_sub_dir' / 'sub_sub.file',
            temp_dir / 'src_tree' / 'sub_dir_2',
            temp_dir / 'dst_tree'
        ]

        for path in make:
            if path.is_file():
                with path.open('w'):
                    pass
            elif path.is_dir():
                path.mkdir()

        # Act
        mimic_folder(src_tree, dst_tree)

        result = []
        for dirpath, _, files in os.walk(dst_tree):
            result.append(Path(dirpath).relative_to(dst_tree))
            for file in files:
                result.append((Path(file).relative_to(dst_tree)))

        # Assert
        src_tree_dirs = [Path(dirpath).relative_to(src_tree) for dirpath, _, _ in os.walk(src_tree)]
        dst_tree_dirs = [Path(dirpath).relative_to(dst_tree) for dirpath, _, _ in os.walk(dst_tree)]
        self.assertEqual(src_tree_dirs, dst_tree_dirs)

