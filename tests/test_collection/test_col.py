# tests/test_collection/test_col.py

"""
    Unit tests for Collection
"""

# Standard library
import os
from unittest import TestCase
from unittest.mock import Mock
from tempfile import TemporaryDirectory
from json.decoder import JSONDecodeError

# Local imports
from source.constants import *
from source.collection.col import Collection
from source.collection.video import Video

# Third-party packages


class UnserializableObject:
    """Used by 'test_save_metadate_unserializable'"""
    def __init__(self):
        value = None


class TestCollection(TestCase):

    def setUp(self) -> None:
        self.test_collection = Collection()
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_video_file_exists(self):
        expected_filename = 'test.vid'
        expected_file_path = os.path.join(self.temp_dir.name, expected_filename)
        expected_root = self.temp_dir.name
        expected_hash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

        with open(expected_file_path, 'w') as file:
            self.test_collection.add_video(file.name)

        added_vid = self.test_collection.videos.get(expected_hash)
        file_data = added_vid.data.get(FILE_DATA)
        result_path = file_data.get(PATH)
        result_root = file_data.get(ROOT)
        result_filename = file_data.get(FILENAME)
        result_hash = file_data.get(HASH)

        self.assertEqual(expected_file_path, result_path)
        self.assertEqual(expected_root, result_root)
        self.assertEqual(expected_filename, result_filename)
        self.assertEqual(expected_hash, result_hash)

    def test_add_video_does_not_exist(self):
        bad_path = os.path.join(self.temp_dir.name, 'does_not_exist.file')
        with self.assertRaises(FileNotFoundError):
            self.test_collection.add_video(bad_path)

    def test_get_video(self):
        expected_value = 'test_value'
        test_hash = 'fake_hash'
        self.test_collection.videos.update({test_hash: expected_value})
        result = self.test_collection.get_video(test_hash)
        self.assertEqual(expected_value, result)

    def test_metadata_save(self):
        test_file_name = 'save.data'
        test_file_path = os.path.join(self.temp_dir.name, test_file_name)
        test_vid_1 = Video()
        test_vid_2 = Video()
        test_vid_1.data.update({"test_key": "test_value"})
        test_vid_2.data.update({"test_key": "test_value"})

        self.test_collection.videos.update({"fake_hash_1": test_vid_1})
        self.test_collection.videos.update({"fake_hash_2": test_vid_2})

        expected_value = """{
    "fake_hash_1": {
        "user_data": {},
        "test_key": "test_value"
    },
    "fake_hash_2": {
        "user_data": {},
        "test_key": "test_value"
    }
}"""

        self.test_collection.metadata_save(test_file_path)
        with open(test_file_path, 'r') as file:
            result = file.read()

        self.assertEqual(expected_value, result)

    def test_metadata_save_file_exists(self):

        test_vid = Video()
        self.test_collection.videos.update({'fake_hash': test_vid})
        bad_filename = 'does_not_exist.file'
        save_file_path = os.path.join(self.temp_dir.name, bad_filename)

        with open(save_file_path, 'w') as file:
            file.write('test data')

        with self.assertRaises(FileExistsError):
            self.test_collection.metadata_save(save_file_path)

    def test_metadata_load_valid(self):
        test_filename = 'load.file'
        test_file_path = os.path.join(self.temp_dir.name, test_filename)

        file_data = """{
    "fake_hash_1": {
        "user_data": {},
        "test_key": "test_value"
    },
    "fake_hash_2": {
        "user_data": {},
        "test_key": "test_value"
    }
}"""

        with open(test_file_path, 'w') as file:
            file.write(file_data)

        self.test_collection.metadata_load(test_file_path)

        expected_value_1 = {
            "user_data": {},
            "test_key": "test_value"
        }

        expected_value_2 = {
            "user_data": {},
            "test_key": "test_value"
        }

        result_1 = self.test_collection.videos.get('fake_hash_1').data
        result_2 = self.test_collection.videos.get('fake_hash_2').data

        self.assertEqual(expected_value_1, result_1)
        self.assertEqual(expected_value_2, result_2)

    def test_metadata_load_invalid(self):
        test_filename = 'invalid.json'
        test_file_path = os.path.join(self.temp_dir.name, test_filename)
        with open(test_file_path, 'w') as file:
            file.write('invalid json data')

        with self.assertRaises(JSONDecodeError):
            self.test_collection.metadata_load(test_file_path)

    def test_metadata_load_does_not_exist(self):
        bad_filename = 'does_not_exist.file'
        bad_path = os.path.join(self.temp_dir.name, bad_filename)
        with self.assertRaises(FileNotFoundError):
            self.test_collection.metadata_load(bad_path)

    def test_scan_files(self):
        test_files = []
        for i in range(3):
            filename = f"test_file{str(i)}.mp4"
            path = os.path.join(self.temp_dir.name, filename)
            with open(path, 'w') as file:
                file.write(str(i))
                test_files.append(file)

        self.test_collection.scan_directory(self.temp_dir.name)

        result = [vid.data.get(FILE_DATA).get(PATH) for vid in self.test_collection.videos.values()]

        for i in range(3):
            cur = test_files.pop().name
            self.assertTrue(cur in result)

    def test_to_json(self):
        test_vid = Video()
        unserializable = UnserializableObject()
        test_vid.data = {'key 1': 'serializable', 'key 2': unserializable}
        test_vide_hash = 'fake_hash'
        self.test_collection.videos.update({test_vide_hash: test_vid})
        expected_value = """{
    "fake_hash": {
        "key 1": "serializable",
        "key 2": "Object 'UnserializableObject' is not serializable"
    }
}"""
        result = self.test_collection.to_json()
        self.assertEqual(expected_value, result)

    def test_update_api_data(self):
        # Arrange
        fake_vid_1 = Video()
        fake_vid_1.data = {
            USER_DATA: {'filename': 'fake_filename_1'},
            FILE_DATA: {}
        }

        fake_vid_2 = Video()
        fake_vid_2.data = {
            USER_DATA: {'filename': 'fake_filename_2'},
            FILE_DATA: {}
        }

        self.test_collection.videos = {'fake_hash_1': fake_vid_1, 'fake_hash_2': fake_vid_2}

        fake_api_1 = Mock()
        fake_api_1.get_required_params.return_value = ['filename']
        fake_api_1.get_name.return_value = 'fake_api_1'
        fake_api_1.fetch_video_data.side_effect = lambda kwargs: {kwargs.get('filename'): kwargs.get('filename') + '_return_data'}

        fake_api_2 = Mock()
        fake_api_2.get_required_params.return_value = ['filename']
        fake_api_2.get_name.return_value = 'fake_api_2'
        fake_api_2.fetch_video_data.side_effect = lambda kwargs: {
            kwargs.get('filename'): kwargs.get('filename') + '_return_data'}

        self.test_collection.api_manager.apis = {'fake_api_1': fake_api_1, 'fake_api_2': fake_api_2}

        # Act
        self.test_collection.update_api_data()

        # Assert
        result_1 = self.test_collection.videos.get('fake_hash_1').data
        self.assertTrue('fake_api_1' in result_1.keys())
        self.assertTrue('fake_api_2' in result_1.keys())
        self.assertTrue(result_1.get('fake_api_1'), 'filename_return_data')
        self.assertTrue(result_1.get('fake_api_2'), 'filename_return_data')

        result_2 = self.test_collection.videos.get('fake_hash_2').data
        self.assertTrue('fake_api_1' in result_2.keys())
        self.assertTrue('fake_api_2' in result_2.keys())
        self.assertTrue(result_2.get('fake_api_1'), 'filename_return_data')
        self.assertTrue(result_2.get('fake_api_2'), 'filename_return_data')
