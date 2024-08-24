# tests/test_datafetchers/test_omdb_api.py

"""
    Unit tests for source/datafetchers/omdb_plugin.py
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock, patch

# Local imports
from source.datafetchers.omdb_plugin import OMDBAPI

# Third-party packages
import requests


class TestOMDBAPI(TestCase):
    def setUp(self) -> None:
        self.mock_response = Mock()
        self.api = OMDBAPI()

    def tearDown(self) -> None:
        pass

    @patch('requests.get')
    def test_fetch_video_data_200_found(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {'Response': 'True'}

        mock_get.return_value = self.mock_response
        data = self.api.fetch_data(title='identifiable title')

        self.assertTrue(type(data) == dict)
        self.assertEqual(data.get('Response'), 'True')

    @patch('requests.get')
    def test_fetch_video_data_200_not_found(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {'Response': 'False', 'Error': 'Movie not found!'}

        mock_get.return_value = self.mock_response
        data = self.api.fetch_data(title='unidentifiable title')

        self.assertTrue(type(data) == dict)
        self.assertEqual(data.get('Response'), 'False')

    @patch('requests.get')
    def test_fetch_video_data_429(self, mock_get):
        self.mock_response.status_code = 429
        self.mock_response.json.return_value = {'Error': self.mock_response.status_code}

        mock_get.return_value = self.mock_response

        with self.assertRaises(requests.HTTPError):
            self.api.fetch_data(title='test title')
