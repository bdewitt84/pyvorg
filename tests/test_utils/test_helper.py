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
