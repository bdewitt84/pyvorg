# tests/test_service/test_collectionservice.py

# Standard library
from unittest import TestCase
from unittest.mock import call, Mock

# Local imports
import service.collectionservice as col_svc

# Third-party packages


class TestCollectionService(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_add_videos(self):
        # Arrange
        mock_collection = Mock()
        mock_vid_1 = Mock()
        mock_vid_2 = Mock()
        videos = [mock_vid_1, mock_vid_2]

        # Act
        col_svc.add_videos(mock_collection, videos)

        # Assert
        mock_collection.add_video_instance.has_calls([call(mock_vid_1), call(mock_vid_2)])

    def test_apply_filter(self):
        # Arrange
        video_1 = Mock()
        video_2 = Mock()

        video_1.get_pref_data.side_effect = lambda x: 'vid_1_' + x
        video_2.get_pref_data.side_effect = lambda x: 'vid_2_' + x

        videos = [video_1, video_2]

        # Act
        result = col_svc.apply_filter(videos, filter_string='title=vid_1_title')

        # Assert
        self.assertIn(video_1, result)
        self.assertNotIn(video_2, result)

    def test_get_metadata(self):
        # TODO: Need to fix Collection.to_dict first
        # Arrange

        # Act

        # Assert
        pass

    def test_get_filtered_videos(self):
        # Arrange
        mock_vid_1 = Mock()
        mock_vid_2 = Mock()

        mock_vid_1.get_pref_data.side_effect = lambda x: 'vid_1_' + x
        mock_vid_2.get_pref_data.side_effect = lambda x: 'vid_2_' + x

        mock_collection = Mock()
        mock_collection.get_videos.return_value = [mock_vid_1, mock_vid_2]

        # Act
        result = col_svc.get_filtered_videos(mock_collection, ['title=vid_1_title'])

        # Assert
        self.assertIn(mock_vid_1, result)
        self.assertNotIn(mock_vid_2, result)

    def test_import_metadata(self):
        # Arrange
        mock_collection = Mock()
        mock_collection.videos = {'base_key': 'base_value'}
        metadata = {'import_key': 'import_value'}

        # Act
        col_svc.import_metadata(mock_collection, metadata)

        # Assert
        self.assertIn('import_key', mock_collection.videos.keys())
        self.assertIn('import_value', mock_collection.videos.values())

    def test_validate_metadata(self):
        # TODO: Implement source; nothing to test
        # Arrange

        # Act

        # Assert
        pass
