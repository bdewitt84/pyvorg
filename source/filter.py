# ./source/utils/filter.py

# Standard library
import re

# Local imports

# Third-party packages


class Filter:
    def __init__(self, key, operator, right_operand):
        self.key = key
        self.operator = operator
        self.right_operand = self.infer_value(right_operand)

    @staticmethod
    def compare_lexical(left, operator, right):
        if operator == "=":
            return left.lower() == right.lower()

        elif operator == "<":
            return left.lower() < right.lower()

        elif operator == ">":
            return left.lower() > right.lower()

        else:
            raise ValueError("Unknown operator")

    @staticmethod
    def compare_numeric(left, operator, right):
        if operator == "=":
            return left == right

        elif operator == "<":
            return left < right

        elif operator == ">":
            return left > right

        else:
            raise ValueError("Unknown operator")

    @staticmethod
    def from_string(string):
        key, operator, value = Filter.parse_filter_string(string)
        return Filter(key, operator, value)

    @staticmethod
    def infer_value(string):
        try:
            return float(string)
        except ValueError:
            pass

        match = re.match(r"\d+", string)
        if match:
            return float(match.group())
        else:
            return string

    def matches(self, left_operand):
        inferred_value = self.infer_value(left_operand)
        if isinstance(inferred_value, (int, float)):
            return self.compare_numeric(inferred_value, self.operator, self.right_operand)
        elif isinstance(inferred_value, str):
            return self.compare_lexical(inferred_value, self.operator, self.right_operand)

    @staticmethod
    def parse_filter_string(string):
        match = re.match(r"(\w+)([<>=])(.+)", string)

        if match is None:
            raise ValueError("Invalid filter string")

        key, operator, value = match.groups()
        return key.lower(), operator, value.lower()
