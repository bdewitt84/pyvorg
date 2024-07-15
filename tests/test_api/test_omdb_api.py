# tests/test_api/test_omdb_api.py

# Standard library
import unittest
from unittest.mock import Mock, patch

import requests

# Local imports
from source.api.omdb_api import OMDBAPI
from source.exceptions import RateLimitExceededError


# Third-party packages


class TestOMDBAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_response = Mock()
        self.api = OMDBAPI()

    def tearDown(self) -> None:
        pass

    @patch('requests.get')
    def test_fetch_video_data_200(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {'Response': 'True'}

        mock_get.return_value = self.mock_response
        data = self.api.fetch_video_data('title')

        self.assertTrue(type(data) == dict)
        self.assertEqual(data.get('Response'), 'True')

    @patch('requests.get')
    def test_fetch_video_data_429(self, mock_get):
        self.mock_response.status_code = 429
        self.mock_response.json.return_value = {'Error': self.mock_response.status_code}

        mock_get.return_value = self.mock_response

        with self.assertRaises(requests.HTTPError):
            self.api.fetch_video_data('title')
