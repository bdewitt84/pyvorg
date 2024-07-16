# ./tests/test_command/test_video_update_data.py

"""
    Unit tests for MoveVideoCommand
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock

# Local imports
from source.collection.video import Video
from source.command.update_video_data import UpdateVideoData
from source.constants import *

# Third-party packages


class TestVideoUpdate(TestCase):

    def setUp(self) -> None:
        self.mock_api_name = 'mock_api'
        self.test_key = 'test_key'
        self.test_value = 'test_value'
        self.mock_api = Mock()
        self.mock_api.get_name.return_value = self.mock_api_name
        self.mock_api.fetch_video_data.return_value = {self.test_key: self.test_value}
        self.test_vid = Video()
        self.test_cmd = UpdateVideoData(self.test_vid, self.mock_api)

    def tearDown(self) -> None:
        pass

    def test_exec(self):
        self.test_cmd.exec()
        expected_value = {self.mock_api_name: {self.test_key: self.test_value}, USER_DATA: {}}
        result = self.test_vid.data
        self.assertEqual(expected_value, result)

    def test_undo(self):
        self.test_cmd.undo_data = {self.test_key: self.test_value}
        self.test_vid.data.update({self.mock_api_name: {'bad_key': 'bad_value'}})
        expected_value = {self.mock_api_name: self.test_cmd.undo_data, USER_DATA: {}}
        self.test_cmd.undo()
        result = self.test_vid.data
        self.assertEqual(expected_value, result)
        self.assertTrue(self.test_cmd.undo_data is None)

    # def test_validate_exec(self):
    #     pass
    #
    # def test_validate_undo(self):
    #     pass