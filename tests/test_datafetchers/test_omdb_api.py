# tests/test_datafetchers/test_omdb_api.py

"""
    Unit tests for source/datafetchers/omdb_plugin.py
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock, patch

# Local imports
from source.datafetchers.omdb_plugin import OMDBFetcher

# Third-party packages
import requests


class TestOMDBAPI(TestCase):
    def setUp(self) -> None:
        self.mock_response = Mock()
        self.api = OMDBFetcher()

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

    def test_get_api_url(self):
        # Arrange
        # Act
        result = self.api.get_api_url()

        # Assert
        self.assertEqual(type(result), str)

    def test_get_omdb_api_key(self):
        # Arrange
        # Act
        result = self.api.get_omdb_api_key()

        # Assert
        self.assertEqual(type(result), str)

    def test_get_optional_params(self):
        # Arrange
        # Act
        result = self.api.get_optional_params()

        # Assert
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(elem, str) for elem in result))

    def test_get_required_params(self):
        # Arrange
        # Act
        result = self.api.get_required_params()

        # Assert
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(elem, str) for elem in result))

    def test_construct_params(self):
        # Arrange
        kwargs = {
            'title': 'kwarg_title',
            'year': 'kwarg_year',
        }

        # Act
        result = self.api._construct_params(kwargs)

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn('t', result.keys())
        self.assertTrue(result.get('t'), 'kwarg_title')
        self.assertIn('y', result.keys())
        self.assertTrue(result.get('y'), 'kwarg_title')

    @patch('source.datafetchers.omdb_plugin.requests.get')
    def test_query_omdb(self, mock_get):
        # Arrange
        params = {}
        response = Mock()
        response.status_code = 200
        response.json.return_value = {'Response': 'True'}
        mock_get.return_value = response

        # Act
        result = self.api._query_omdb(params)

        # Assert
        self.assertEqual({'Response': 'True'}, result)
