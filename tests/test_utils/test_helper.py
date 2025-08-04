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

    def test_create_dummy_files(self):
        # Arrange
        target_path = Path(self.temp_dir.name)

        # Act
        create_dummy_files(target_path, 3, lambda x: 'dummy_video_' + str(x) + '.mp4')

        # Assert
        expected = [
            Path(target_path) / 'dummy_video_0.mp4',
            Path(target_path) / 'dummy_video_1.mp4',
            Path(target_path) / 'dummy_video_2.mp4'
        ]

        result = [file for file in target_path.iterdir()]

        for path in expected:
            self.assertIn(path, result)

    def test_default_serializer(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_fill_kwargs_from_metadata(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_find_missing_params(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_get_preferred_source(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_logger_init(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_timestamp_generate(self):
        # TODO: Implement
        pass

    def test_timestamp_validate(self):
        # Arrange
        valid_timestamp = '2000-01-01 01:00:00'
        invalid_timestamp = '01:00:00 2000-01-01'

        # Act and assert
        self.assertTrue(timestamp_validate(valid_timestamp))
        self.assertFalse(timestamp_validate(invalid_timestamp))

    def test_update_api_data(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass
