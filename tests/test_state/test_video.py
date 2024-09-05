# source/test_state/test_video.py

"""
    Unit tests for source/collection/video.py
"""

# Standard library
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from unittest import TestCase

# Local imports
from source.constants import *
from source.state.video import Video


# Third-party packages


class TestVideo(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.temp_vid_filename = 'temp.vid'
        self.temp_vid_path = os.path.join(self.temp_dir.name, self.temp_vid_filename)
        with open(self.temp_vid_path, 'w') as file:
            file.write('test data')

        temp_vid_data = {
            "user_data": {},
            "file_data": {
                "path": self.temp_vid_path,
                "root": self.temp_dir.name,
                "filename": self.temp_vid_filename,
                "hash": "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9",
                "timestamp": "1970-01-01 00:00:01"
            }
        }

        self.test_vid = Video()
        self.test_vid.data = temp_vid_data

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_append_available_sources(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_from_file(self):
        # Arrange
        filename = 'test.file'
        path = Path(self.temp_dir.name) / filename
        path.touch()

        # Act
        result = Video.from_file(path)

        # Assert
        self.assertEqual(result.get_path(), path)

    def test_get_filename(self):
        result = self.test_vid.get_filename()
        expected_filename = self.temp_vid_filename
        self.assertEqual(expected_filename, result)

    def test_get_hash(self):
        result = self.test_vid.get_hash()
        expected_hash = '916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9'
        self.assertEqual(expected_hash, result, f"Should be '{expected_hash}'.")

    def test_get_path(self):
        # Act
        result = self.test_vid.get_path()

        # Assert
        expected_path = Path(self.temp_vid_path)
        self.assertEqual(expected_path, result)

    def test_get_pref_data(self):
        # Todo: mock the call to get preferred sources, or just refactor as a parameter
        key = 'test_key'
        expected_value = 'pass'
        self.test_vid.data = {
            USER_DATA: {key: expected_value},
            OMDB_DATA: {key: 'fail'},
            GUESSIT_DATA: {key: 'fail'}
        }
        result = self.test_vid.get_pref_data(key)
        self.assertEqual(expected_value, result)

        self.test_vid.data = {
            USER_DATA: {},
            OMDB_DATA: {key: expected_value},
            GUESSIT_DATA: {key: 'fail'}
        }
        result = self.test_vid.get_pref_data(key)
        self.assertEqual(expected_value, result)

        self.test_vid.data = {
            USER_DATA: {},
            OMDB_DATA: {},
            GUESSIT_DATA: {key: expected_value}
        }
        result = self.test_vid.get_pref_data(key)
        self.assertEqual(expected_value, result)

    def test_get_root(self):
        # Todo: take a better look at testing paths vs strings here
        result = self.test_vid.get_root()
        expected_root = self.temp_dir.name
        self.assertEqual(expected_root, str(result))

    def test_get_source_data_no_key(self):
        api_name = 'test_api'
        expected = {'test_key': 'test_value'}
        self.test_vid.data.update({api_name: expected})
        self.test_vid.get_source_data(api_name)
        result = self.test_vid.get_source_data(api_name)
        self.assertEqual(expected, result)

    def test_get_source_data_with_key(self):
        api_name = 'test_api'
        key = 'test_key'
        expected_value = 'test_value'
        api_data = {key: expected_value}
        self.test_vid.data.update({api_name: api_data})
        result = self.test_vid.get_source_data(api_name, key)
        self.assertEqual(expected_value, result)

    def test_get_source_keys(self):
        # Arrange
        self.test_vid.data = {
            'source_1': {
                'source_1_key_1': 'source_1_val_1',
                'source_1_key_2': 'source_1_val_2'
            },
            'source_2': {
                'source_2_key_1': 'source_2_val_1',
                'source_2_key_2': 'source_2_val_2'
            }
        }

        # Act
        result = self.test_vid.get_source_keys()

        # Assert
        self.assertEqual(['source_1_key_1', 'source_1_key_2', 'source_2_key_1', 'source_2_key_2'], result)

    def test_get_source_names(self):
        # Arrange
        self.test_vid.data = {
            'source_1': {
                'source_1_key_1': 'source_1_val_1',
                'source_1_key_2': 'source_1_val_2'
            },
            'source_2': {
                'source_2_key_1': 'source_2_val_1',
                'source_2_key_2': 'source_2_val_2'
            }
        }

        # Act
        result = self.test_vid.get_source_names()

        # Assert
        self.assertEqual(['source_1', 'source_2'], result)

    def test_get_user_data(self):
        key = 'test_key'
        expected_value = 'test_value'
        self.test_vid.data.update({
            'user_data': {
                key: expected_value}
            }
        )
        result = self.test_vid.get_user_data(key)
        self.assertEqual(expected_value, result)

    def test_set_hash(self):
        # Arrange
        hash_value = 'fake_hash'

        # Act
        self.test_vid.set_hash(hash_value)

        # Assert
        self.assertEqual(hash_value, self.test_vid.get_hash())

    def test_set_source_data(self):
        api_name = 'test_api'
        data = {'test_key': 'test_value'}
        self.test_vid.data.update({api_name: data})
        self.test_vid.set_source_data(api_name, data)
        result = self.test_vid.data.get(api_name)
        self.assertEqual(data, result)

    def test_set_user_data(self):
        key = 'test_key'
        value = 'test_value'
        self.test_vid.set_user_data(key, value)
        expected_data = {key: value}
        result = self.test_vid.data.get(USER_DATA)
        self.assertEqual(expected_data, result)

    def test_to_dict(self):
        # Arrange
        self.test_vid.data = {'test_key': 'test_value'}

        # Act
        result = self.test_vid.to_dict()

        # Assert
        self.assertEqual('test_value', result.get('test_key'))

    @patch('source.state.video.hash_sha256')
    @patch('source.state.video.timestamp_generate')
    def test_update_file_data(self, mock_timestamp_generate, mock_hash_sha256):
        # Arrange
        test_file = Path(self.temp_dir.name, 'fake.file')
        with test_file.open('w') as file:
            file.write('dummy data')
        mock_hash_sha256.return_value = 'fake hash'
        mock_timestamp_generate.return_value = 'fake timestamp'

        # Act
        self.test_vid.update_file_data(test_file)

        # Assert
        expected = {
                PATH: str(test_file),
                ROOT: str(test_file.parent),
                FILENAME: test_file.name,
                HASH: 'fake hash',
                TIMESTAMP: 'fake timestamp'
            }
        self.assertEqual(expected, self.test_vid.data[FILE_DATA])

    def test_update_hash(self):
        with open(self.temp_vid_path, 'w') as file:
            file.write('test data 2')
        self.test_vid.update_hash()
        expected_hash = '26637da1bd793f9011a3d304372a9ec44e36cc677d2bbfba32a2f31f912358fe'
        result = self.test_vid.data.get(FILE_DATA).get(HASH)
        self.assertEqual(expected_hash, result)
