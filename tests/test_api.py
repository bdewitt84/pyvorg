# tests/test_api.py

"""
Unit tests for source/api.py
"""

# Standard library
import unittest
from unittest.mock import Mock, patch

# Local imports
from source.api import *


class TestGetOMDBData(unittest.TestCase):

    @patch('requests.get')
    def test_get_omdb_data_success(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Title": "Three Outlaw Samurai",
            "Response": "True"
        }

        mock_requests_get.return_value = mock_response

        result = get_omdb_data('Three Outlaw Samurai')

        self.assertEqual(result, {"Title": "Three Outlaw Samurai", "Response": "True"})

    @patch('requests.get')
    def test_get_omdb_data_bad_title(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Movie not found!"
        }

        mock_requests_get.return_value = mock_response

        result = get_omdb_data('bogusmovietitle')

        self.assertIsNone(result)

# TODO: Rewrite for Video.update_omdb()
# class TestUpdateOMDBData(unittest.TestCase):
#
#     @patch('api.get_omdb_data')
#     @patch('helper.guess_title')
#     def test_update_omdb_data_valid(self, mock_guess_title, mock_get_omdb_data):
#
#         mock_guess_title.return_value = 'Movie Title'
#
#         mock_get_omdb_data.return_value = {
#             "Title": "Movie Title",
#             "Response": "True"
#         }
#
#         expected_video = {
#             FILE_DATA: {
#                 FILENAME: "Mock_Video.mp4"
#             },
#             OMDB_DATA: {
#                 "Title": "Movie Title",
#                 "Response": "True"
#             }
#         }
#
#         mock_video = {
#             FILE_DATA: {
#                 FILENAME: "Mock_Video.mp4"
#             }
#         }
#
#         update_video_omdb_data(mock_video, 'Movie Title')
#
#         self.assertEqual(expected_video, mock_video)
