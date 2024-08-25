# tests/test_datafetchers/test_base_fetcher.py

"""
    Unit tests for base_fetcher.py
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock

# Local imports
from source.datafetchers.base_fetcher import DataFetcher

# Third-party packages


class TestDataFetcher(TestCase):

    def setUp(self) -> None:
        class SubClass(DataFetcher):
            def __init__(self):
                super().__init__()

            def fetch_data(self, **kwargs):
                super().fetch_data()

            def get_optional_params(self):
                super().get_optional_params()

            def get_required_params(self):
                super().get_required_params()

        self.SubClass = SubClass
        self.subclass = SubClass()

    def tearDown(self) -> None:
        pass

    def test_fetch_data(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.fetch_data()

    def test_get_name(self):
        # Arrange
        # Act
        result = self.subclass.get_name()
        # Assert
        self.assertEqual('SubClass', result)

    def test_get_optional_params(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.get_optional_params()

    def test_get_required_params(self):
        # Arrange
        # Act
        # Assert
        with self.assertRaises(NotImplementedError):
            self.subclass.get_required_params()
