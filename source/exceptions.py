# source/exceptions.py

"""
Custom exceptions for use within the package
"""


class RateLimitExceededError(Exception):
    def __init__(self):
        super().__init__("Rate limit exceeded.")


class ValidationError(Exception):
    pass
