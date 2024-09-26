# tests/test_service/test_videoservice.py

# Standard library
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch, Mock

# Local imports
from source.utils import videoutils
from source.utils.helper import create_dummy_files

# Third-party packages
# n\a


class TestVideoService(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_from_file(self):
        # Arrange
        filename = 'test.file'
        path = Path(self.temp_dir.name) / filename
        path.touch()

        # Act
        result = videoutils.create_video_from_file_path(path)

        # Assert
        self.assertEqual(result.get_path(), path)

    def test_create_videos_from_file_paths(self):
        # Arrange
        files = create_dummy_files(self.temp_dir.name, 3, lambda x: 'test_file_' + str(x) + '.mp4')

        # Act
        result = videoutils.create_videos_from_file_paths(files)

        # Assert
        self.assertTrue(any(files[0] == video.get_path() for video in result))
        self.assertTrue(any(files[1] == video.get_path() for video in result))
        self.assertTrue(any(files[2] == video.get_path() for video in result))
        self.assertFalse(any('not_a_real_path' == video.get_path() for video in result))

    @patch.object(videoutils, 'generate_str_from_metadata')
    def test_generate_destination_paths(self, mock_generate_str):
        # Arrange
        mock_vid_1 = Mock()
        mock_vid_2 = Mock()

        mock_vid_1.name = 'vid_1'
        mock_vid_2.name = 'vid_2'

        mock_generate_str.side_effect = lambda x, y: y + '_' + x.name

        videos = [mock_vid_1, mock_vid_2]

        # Act
        result = videoutils.generate_destination_paths(videos, Path('fake_dest_tree'), 'format_str')

        # Assert
        expected = [
            Path('fake_dest_tree/format_str_vid_1'),
            Path('fake_dest_tree/format_str_vid_2')
        ]
        self.assertEqual(expected, result)

    def test_generate_str_from_metadata(self):
        # Arrange
        mock_vid = Mock()
        mock_vid.get_pref_data.side_effect = lambda x, y: x + '_return'

        # Act
        result = videoutils.generate_str_from_metadata(mock_vid, '%title (%year)')

        # Assert
        self.assertEqual('title_return (year_return)', result)

    def test_build_cmd_kwargs(self):
        # Arrange
        video_1 = Mock()
        video_2 = Mock()

        video_1.get_pref_data.side_effect = lambda x: x + '_return'
        video_2.get_pref_data.side_effect = lambda x: x + '_return'

        videos = [video_1, video_2]

        req_params = ['param_1', 'param_2']

        # Act
        result = videoutils.build_cmd_kwargs(videos, req_params)

        # Assert
        self.assertIn({'param_1': 'param_1_return', 'param_2': 'param_2_return'}, result)
        self.assertIn({'param_1': 'param_1_return', 'param_2': 'param_2_return'}, result)
