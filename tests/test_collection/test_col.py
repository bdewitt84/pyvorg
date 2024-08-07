# tests/test_collection/test_col.py

"""
    Unit tests for Collection
"""

# Standard library
import os
from pathlib import Path
from json.decoder import JSONDecodeError
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, Mock, patch

# Local imports
from source.collection.col import Collection

# Third-party packages
# n/a


class UnserializableObject:
    """Used by 'test_save_metadate_unserializable'"""
    def __init__(self):
        pass


class TestCollection(TestCase):

    def setUp(self) -> None:
        self.test_collection = Collection()
        self.test_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.test_dir.cleanup()

    @patch('source.collection.col.Video.from_file')
    def test_add_video_file_exists(self, mock_from_file):
        # Arrange
        path = Path('fake path')
        test_video = Mock()
        test_video.get_hash.return_value = 'fake hash'
        mock_from_file.return_value = test_video

        # Act
        self.test_collection.add_video(path)

        # Assert
        mock_from_file.called_once_with(path)
        self.assertEqual(self.test_collection.videos, {'fake hash': test_video})

    def test_add_video_does_not_exist(self):
        # Arrange
        bad_path = Path(self.test_dir.name, 'does_not_exist.fil')

        # Act and Assert
        with self.assertRaises(FileNotFoundError):
            self.test_collection.add_video(bad_path)

    @patch('source.collection.col.Filter.from_string')
    def test_apply_filter(self, mock_from_string):
        # Arrange
        test_video_1 = Mock()
        test_video_2 = Mock()

        test_video_1.get_pref_data.return_value = "match"
        test_video_2.get_pref_data.return_value = "not a match"

        videos = [test_video_1, test_video_2]

        test_filter = Mock()
        test_filter.matches.side_effect = lambda x: True if x == "match" else False
        mock_from_string.return_value = test_filter

        test_filter_string = "test filter string"

        # Act
        result = self.test_collection.apply_filter(videos, test_filter_string)

        # Assert
        mock_from_string.assert_called_once_with(test_filter_string)
        self.assertTrue(test_video_1 in result, "'test_video_1' should be in the result")
        self.assertTrue(test_video_2 not in result, "'test_video_2' should not be in the result")

    def test_get_video(self):
        expected_value = 'test_value'
        test_hash = 'fake_hash'
        self.test_collection.videos.update({test_hash: expected_value})
        result = self.test_collection.get_video(test_hash)
        self.assertEqual(expected_value, result)

    def test_get_videos(self):
        # Arrange
        video_1 = Mock()
        video_2 = Mock()
        videos = {
            "hash_1": video_1,
            "hash_2": video_2
        }

        self.test_collection.videos = videos

        # Act
        result = self.test_collection.get_videos()

        # Assert
        self.assertTrue(len(result) == 2)
        self.assertTrue(video_1 in result)
        self.assertTrue(video_2 in result)

    @patch('source.collection.col.Collection.apply_filter')
    def test_get_videos_with_filter(self, mock_filter_videos):
        # Arrange
        test_filter_string = "test filter string"
        mock_filter_videos.return_value = None
        test_vid_1 = Mock()
        self.test_collection.videos = {"video 1": test_vid_1}

        # Act
        self.test_collection.get_videos([test_filter_string])

        # Assert
        # Note that dict values are not directly comparable, so we work around it by
        # converting the dict values to a list
        mock_filter_videos.assert_called_once()
        self.assertEqual(list(mock_filter_videos.call_args.args[0]), [test_vid_1])
        self.assertEqual(mock_filter_videos.call_args.args[1], test_filter_string)

    def test_metadata_save(self):
        # Arrange
        test_file_name = 'save.data'
        test_file_path = Path(self.test_dir.name, test_file_name)

        test_vid_1 = Mock()
        test_vid_2 = Mock()

        test_vid_1.data = {"test_key": "test_value"}
        test_vid_2.data = {"test_key": "test_value"}

        test_vid_1.get_hash.return_value = "fake_hash_1"
        test_vid_2.get_hash.return_value = "fake_hash_2"

        self.test_collection.videos = {
            "fake_hash_1": test_vid_1,
            "fake_hash_2": test_vid_2
        }

        print(self.test_collection.to_dict())

        # Act
        self.test_collection.metadata_save(test_file_path)

        # Assert
        expected_value = """{
    "fake_hash_1": {
        "test_key": "test_value"
    },
    "fake_hash_2": {
        "test_key": "test_value"
    }
}"""

        with open(test_file_path, 'r') as file:
            result = file.read()

        self.assertEqual(expected_value, result)

    def test_metadata_load_valid(self):
        test_filename = 'load.file'
        test_file_path = os.path.join(self.test_dir.name, test_filename)

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
        test_file_path = os.path.join(self.test_dir.name, test_filename)
        with open(test_file_path, 'w') as file:
            file.write('invalid json data')

        with self.assertRaises(JSONDecodeError):
            self.test_collection.metadata_load(test_file_path)

    def test_metadata_load_does_not_exist(self):
        bad_filename = 'does_not_exist.file'
        bad_path = os.path.join(self.test_dir.name, bad_filename)
        with self.assertRaises(FileNotFoundError):
            self.test_collection.metadata_load(bad_path)

    def test_scan_directory(self):
        test_files = []
        for i in range(3):
            filename = f"test_file{str(i)}.mp4"
            path = os.path.join(self.test_dir.name, filename)
            with open(path, 'w') as file:
                file.write(str(i))
                test_files.append(file)

        self.test_collection.scan_directory(self.test_dir.name)

        result = [vid.data.get(FILE_DATA).get(PATH) for vid in self.test_collection.videos.values()]

        for i in range(3):
            cur = test_files.pop().name
            self.assertTrue(cur in result)

    def test_scan_file(self):
        # Arrange
        test_filename = 'test_file.mp4'
        test_file_path = os.path.join(self.test_dir.name, test_filename)
        with open(test_file_path, 'w') as file:
            file.write('dummy_data')

        # Act
        self.test_collection.scan_file(test_file_path)

        # Assert
        result = [vid.data.get(FILE_DATA).get(PATH) for vid in self.test_collection.videos.values()]
        self.assertTrue(test_file_path in result)

    @patch('source.collection.col.Collection.scan_path_list')
    @patch('source.collection.col.glob')
    def test_scan_glob(self, mock_glob, mock_scan_path_list):
        # Arrange
        expected_list = [
            "list item 1",
            "list item 2"
        ]
        mock_glob.return_value = expected_list

        # Act
        self.test_collection.scan_glob("./glob_string.*")

        # Assert
        mock_scan_path_list.assert_called_once_with(expected_list)

    @patch('source.collection.col.Collection.scan_directory')
    @patch('source.collection.col.Collection.scan_file')
    def test_scan_path_file(self, mock_scan_file, mock_scan_directory):
        # Arrange
        filename = 'test_video.mp4'
        path = os.path.join(self.test_dir.name, filename)

        with open(path, 'w') as file:
            file.write('dummy data')

        args = Mock()
        args.command = 'scan'
        args.path = path

        # Act
        self.test_collection.scan_path(path)

        # Assert
        mock_scan_file.assert_called_once_with(path)
        mock_scan_directory.assert_not_called()

    @patch('source.collection.col.Collection.scan_directory')
    @patch('source.collection.col.Collection.scan_file')
    def test_scan_path_directory(self, mock_scan_file, mock_scan_directory):
        # Arrange
        path = self.test_dir.name

        args = Mock()
        args.command = 'scan'
        args.path = path

        # Act
        self.test_collection.scan_path(path)

        # Assert
        mock_scan_directory.assert_called_once_with(path)
        mock_scan_file.assert_not_called()

    @patch('source.collection.col.Collection.scan_path')
    def test_scan_path_list(self, mock_scan_path):
        # Arrange
        path_1 = "path 1"
        path_2 = "path 2"

        path_list = [
            path_1,
            path_2
        ]

        # Act
        self.test_collection.scan_path_list(path_list)

        # Assert
        mock_scan_path.assert_any_call(path_1)
        mock_scan_path.assert_any_call(path_2)

    @patch('source.collection.col.Collection.scan_directory')
    @patch('source.collection.col.Collection.scan_file')
    def test_scan_path_invalid(self, mock_scan_file, mock_scan_directory):
        # Arrange
        path = 'invalid path'

        args = Mock()
        args.command = 'scan'
        args.path = path

        # Act
        with self.assertRaises(ValueError):
            self.test_collection.scan_path(path)

        # Assert
        mock_scan_directory.assert_not_called()
        mock_scan_file.assert_not_called()

    @patch('source.collection.col.Collection.get_videos')
    def test_to_dict(self, mock_get_videos):
        # Arrange
        video_1 = Mock()
        video_2 = Mock()

        video_1.data = {"test key 1": "test data 1"}
        video_2.data = {"test key 2": "test data 2"}

        video_1.get_hash.return_value = "hash_1"
        video_2.get_hash.return_value = "hash_2"

        mock_get_videos.return_value = [
            video_1,
            video_2
        ]

        # Act
        result = self.test_collection.to_dict()

        print(result)

        # Assert
        mock_get_videos.assert_called_once_with(None)
        expected_result = {
            "hash_1": {"test key 1": "test data 1"},
            "hash_2": {"test key 2": "test data 2"}
        }

        self.assertEqual(expected_result, result)

    def test_to_json(self):
        # Arrange
        test_vid = Mock()
        test_vid.get_hash.return_value = "fake_hash"
        unserializable = UnserializableObject()
        test_vid.data = {'key 1': 'serializable', 'key 2': unserializable}
        test_vide_hash = 'fake_hash'
        self.test_collection.videos = {
            test_vide_hash: test_vid
        }

        # Act
        result = self.test_collection.to_json()

        # Assert
        expected_value = """{
    "fake_hash": {
        "key 1": "serializable",
        "key 2": "Object 'UnserializableObject' is not serializable"
    }
}"""
        self.assertEqual(expected_value, result)

    def test_update_api_data(self):
        # Arrange
        test_vid_1 = Mock()
        test_vid_1.update_api_data.return_value = 'return data 1'
        test_vid_2 = Mock()
        test_vid_2.update_api_data.return_value = 'return data 2'

        test_api = Mock()

        self.test_collection.videos.update({'test_vid_1_key': test_vid_1})
        self.test_collection.videos.update({'test_vid_2_key': test_vid_2})

        # Act
        self.test_collection.update_api_data(test_api)

        # Assert
        test_vid_1.update_api_data.assert_called_with(test_api)
        test_vid_2.update_api_data.assert_called_with(test_api)
