# ./tests/test_command/test_updatemetadata_cmd.py

"""
    Unit tests for MoveVideoCommand
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock

# Local imports
from source.state.mediafile import MediaFile
from source.commands.updatemetadata_cmd import UpdateVideoData
from source.constants import *

# Third-party packages


class TestVideoUpdate(TestCase):

    def setUp(self) -> None:
        self.mock_api_name = 'mock_api'
        self.test_key = 'test_key'
        self.test_value = 'test_value'
        self.mock_api = Mock()
        self.mock_api.get_name.return_value = self.mock_api_name
        self.mock_api.fetch_data.return_value = 'return_fetch_data'
        self.test_vid = MediaFile()
        self.test_cmd = UpdateVideoData(self.test_vid, self.mock_api)

    def tearDown(self) -> None:
        pass

    def test_exec(self):
        # Arrange
        test_video = Mock()
        test_video.get_source_data.return_value = 'return_source_data'
        self.test_cmd.video = test_video

        # Act
        self.test_cmd.exec()

        # Assert
        test_video.set_source_data.assert_called_once_with('mock_api', 'return_fetch_data')
        self.assertEqual(self.test_cmd.undo_data, 'return_source_data')

    def test_undo(self):
        self.test_cmd.undo_data = {self.test_key: self.test_value}
        self.test_vid.data.update({self.mock_api_name: {'bad_key': 'bad_value'}})
        expected_value = {self.mock_api_name: self.test_cmd.undo_data, USER_DATA: {}}
        self.test_cmd.undo()
        result = self.test_vid.data
        self.assertEqual(expected_value, result)
        self.assertTrue(self.test_cmd.undo_data is None)

    def test_validate_exec(self):
        # TODO: Implement in source
        # Arrange
        # Act
        # Assert
        pass

    def test_validate_undo(self):
        # TODO: Implement in source
        # Arrange
        # Act
        # Assert
        pass
