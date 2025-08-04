# tests/test_datafetchers/test_guessit_api.py

"""
    Unit tests for GuessitAPI
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock

# Local imports
from source.datasources.guessit_plugin import GuessitAPI

# Third-party packages


class TestGuessitAPI(TestCase):

    def setUp(self) -> None:
        self.test_filename = 'Alien.1979.1080p.BRrip.x264.GAZ.YIFY.mp4'
        self.test_api = GuessitAPI()

    def tearDown(self) -> None:
        pass

    def test_fetch_data(self):
        result = self.test_api.fetch_data(filename=self.test_filename)
        expected_value = {
            'title': 'Alien',
            'year': 1979,
            'screen_size': '1080p',
            'source': 'Blu-ray',
            'other': ['Reencoded', 'Rip'],
            'video_codec': 'H.264',
            'release_group': 'GAZ.YIFY',
            'container': 'mp4',
            'mimetype': 'video/mp4',
            'type': 'movie'}
        self.assertEqual(expected_value, result)

    def test_get_api_name(self):
        result = self.test_api.get_name()
        expected_value = "GuessitAPI"
        self.assertEqual(expected_value, result)

    def test_get_required_params(self):
        result = self.test_api.get_required_params()
        expected_value = ['filename']
        self.assertEqual(expected_value, result)

    def test_get_optional_params(self):
        result = self.test_api.get_optional_params()
        expected_value = None
        self.assertEqual(expected_value, result)
