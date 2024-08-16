# tests/test_collection/test_col.py

"""
    Unit tests for Collection
"""

# Standard library
from pathlib import Path
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

    def test_add_file(self):
        # Arrange
        filename = 'test.mp4'
        filepath = Path(self.test_dir.name) / filename
        filepath.touch()

        # Act
        self.test_collection.add_file(filepath)

        # Assert
        self.assertTrue(filepath in video.data['file_data']['path'] for video in self.test_collection.videos.keys())

    @patch('source.collection.col.Collection.add_file')
    def test_add_files(self, mock_add_file):
        # Arrange
        path_1 = Path('fake_path_1')
        path_2 = Path('fake_path_2')
        path_3 = Path('fake_path_3')
        files = [
            path_1,
            path_2,
            path_3
        ]

        # Act
        self.test_collection.add_files(files)

        # Assert
        mock_add_file.assert_has_calls([call(path_1), call(path_2), call(path_3)])

    @patch('source.collection.col.Video.from_file')
    def test_add_video_file_exists(self, mock_from_file):
        # Arrange
        path = Path('fake path')
        test_video = Mock()
        test_video.get_hash.return_value = 'fake hash'
        mock_from_file.return_value = test_video

        # Act
        self.test_collection.add_video_file(path)

        # Assert
        mock_from_file.called_once_with(path)
        self.assertEqual(self.test_collection.videos, {'fake hash': test_video})

    def test_add_video_does_not_exist(self):
        # Arrange
        bad_path = Path(self.test_dir.name, 'does_not_exist.fil')

        # Act and Assert
        with self.assertRaises(FileNotFoundError):
            self.test_collection.add_video_file(bad_path)

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

    @patch('source.collection.col.Video.from_dict')
    def test_from_dict(self, mock_video_from_dict):
        # Arrange
        test_vid_dict = {'test_key': 'test_value'}
        test_col_dict = {'test_id': test_vid_dict}

        # Act
        result = Collection.from_dict(test_col_dict)

        # Assert
        mock_video_from_dict.assert_has_calls([call(test_vid_dict)])
        self.assertTrue(self.test_collection.videos.get('test_id'))

    @patch('source.collection.col.Collection.from_dict')
    def test_from_json(self, mock_from_dict):
        # Arrange
        test_json_string = r'{"test_key": "test_value"}'

        # Act
        self.test_collection.from_json(test_json_string)

        # Assert
        expected_dict = {'test_key': 'test_value'}
        mock_from_dict.assert_called_once_with(expected_dict)

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

    def test_remove_from_collection(self):
        # Arrange
        vid_dont_remove = Mock()
        vid_remove = Mock()

        self.test_collection.videos = {
            'fake_key_1': vid_dont_remove,
            'fake_key_2': vid_remove
        }

        # Act
        self.test_collection.remove_from_collection([vid_remove])

        # Assert
        self.assertTrue(vid_remove not in self.test_collection.videos.values())
        self.assertTrue(vid_dont_remove in self.test_collection.videos.values())

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

    def test_to_graph(self):
        # TODO: Implement
        pass

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

    def test_to_tsv(self):
        # TODO: Implement
        pass
