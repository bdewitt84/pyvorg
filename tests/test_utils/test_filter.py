# ./tests/test_utils/test_filter.py

"""
    Unit tests for Filter class
"""

# Standard library
from unittest import TestCase
from unittest.mock import patch

# Local imports
from source.filter import Filter

# Third-party packages
# n\a


class TestFilter(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_compare_lexical(self):
        # Assert
        self.assertTrue(Filter.compare_lexical("a", "<", "b"))
        self.assertFalse(Filter.compare_lexical("a", ">", "b"))
        self.assertTrue(Filter.compare_lexical("a", "=", "a"))
        self.assertFalse(Filter.compare_lexical("a", "=", "b"))

    def test_compare_numeric(self):
        # Assert
        self.assertTrue(Filter.compare_numeric(1, "<", 2))
        self.assertFalse(Filter.compare_numeric(1, ">", 2))
        self.assertTrue(Filter.compare_numeric(1, "=", 1))
        self.assertFalse(Filter.compare_numeric(1, "=", 2))

    @patch('source.filter.Filter.parse_filter_string', return_value=("key", "op", "val"))
    def test_from_String(self, mock_parse):
        # Arrange
        test_string = "test_string"

        # Act
        test_filter = Filter.from_string(test_string)

        # Assert
        mock_parse.assert_called_once_with(test_string)
        self.assertEqual(test_filter.key, "key")
        self.assertEqual(test_filter.operator, "op")
        self.assertEqual(test_filter.right_operand, "val")

    def test_infer_value(self):
        # Assert
        self.assertEqual(1970.0, Filter.infer_value("1970"))
        self.assertEqual("test value", Filter.infer_value("test value"))
        self.assertEqual(1970.0, Filter.infer_value("1970 then some text"))
        self.assertEqual("some text then 1970", Filter.infer_value("some text then 1970"))

    def test_matches(self):
        # Arrange
        test_filter_1 = object.__new__(Filter)
        test_filter_1.key = "test_key"
        test_filter_1.operator = "<"
        test_filter_1.right_operand = 1970.0

        test_filter_2 = object.__new__(Filter)
        test_filter_2.key = "test_key"
        test_filter_2.operator = "="
        test_filter_2.right_operand = "test string"

        # Assert
        self.assertTrue(test_filter_1.matches("1969"))
        self.assertFalse(test_filter_1.matches("1970"))
        self.assertFalse(test_filter_1.matches("1971"))
        self.assertTrue(test_filter_2.matches("test string"))
        self.assertFalse(test_filter_2.matches("test_string"))

    def test_parse_filter_string(self):
        # Assert
        self.assertEqual(("year", "<", "1970"), Filter.parse_filter_string("year<1970"))
        self.assertEqual(("title", "=", "name of movie"), Filter.parse_filter_string("title=name of movie"))
        self.assertEqual(("rating", ">", "8.0"), Filter.parse_filter_string("rating>8.0"))

    def test_parse_filter_string_invalid(self):
        # Assert
        with self.assertRaises(ValueError):
            Filter.parse_filter_string("invalid filter string")
