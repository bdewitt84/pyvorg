# tests/test_state/test_col.py

"""
    Unit tests for Collection
"""

# Standard library
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, Mock, patch

# Local imports
from source.state.col import Collection

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

    @patch('source.state.col.Collection.add_file')
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
        mock_add_file.assert_has_calls([call(path_1), call(path_2), call(path_3)], any_order=True)

    @patch('source.state.col.Video.from_file')
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

    def test_add_video_file_does_not_exist(self):
        # Arrange
        bad_path = Path(self.test_dir.name, 'does_not_exist.fil')

        # Act and Assert
        with self.assertRaises(FileNotFoundError):
            self.test_collection.add_video_file(bad_path)

    def test_add_video_instance(self):
        # Arrange
        mock_video = Mock()
        mock_video.get_id.return_value = 'vid_id'

        # Act
        self.test_collection.add_video_instance(mock_video)

        # Assert
        self.assertIn(mock_video, self.test_collection.get_videos())

    # @patch('source.state.col.Collection.generate_video_id')
    # def test_from_dict(self, mock_generate_video_id):
    #     # Arrange
    #     test_dict = {
    #         'fake_hash_1': {
    #             'video_data': 'video_1_data'
    #             },
    #         'fake_hash_2': {
    #             'video_data': 'video_2_data'
    #         }
    #     }
    #     mock_generate_video_id.side_effect = lambda x: x.data.get('video_data')
    #
    #     # Act
    #     result = Collection.from_dict(test_dict)
    #
    #     # Assert
    #     self.assertEqual(2, len(result.videos))
    #     self.assertIn('video_1_data', result.videos.keys())
    #     self.assertIn('video_2_data', result.videos.keys())

    def test_generate_video_id(self):
        # Arrange
        mock_video = Mock()
        mock_video.get_hash.return_value = 'fake_hash'

        # Act
        result = self.test_collection.generate_video_id(mock_video)

        # Assert
        self.assertEqual('fake_hash', result)

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

    @patch('source.state.col.Collection.get_videos')
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

        # Assert
        mock_get_videos.assert_called_once()
        expected_result = {
            "hash_1": {"test key 1": "test data 1"},
            "hash_2": {"test key 2": "test data 2"}
        }

        self.assertEqual(expected_result, result)

#     def test_to_json(self):
#         # Arrange
#         test_vid = Mock()
#         test_vid.get_hash.return_value = "fake_hash"
#         unserializable = UnserializableObject()
#         test_vid.data = {'key 1': 'serializable', 'key 2': unserializable}
#         test_vide_hash = 'fake_hash'
#         self.test_collection.videos = {
#             test_vide_hash: test_vid
#         }
#
#         # Act
#         result = self.test_collection.to_json()
#
#         # Assert
#         expected_value = """{
#     "fake_hash": {
#         "key 1": "serializable",
#         "key 2": "Object 'UnserializableObject' is not serializable"
#     }
# }"""
#         self.assertEqual(expected_value, result)
