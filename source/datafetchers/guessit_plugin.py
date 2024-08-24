# source/datafetchers/guessit_plugin.py

"""
    API interface for Guessit

    This module defines the GuessitAPI class, which provides methods for fetching video data
    from the Guessit, a python library that extracts as much information as possible from a
    video filename.

    Docs:
        https://guessit.readthedocs.io/en/latest/
"""

from guessit import guessit

# Standard library

# Local imports
from source.datafetchers.base_fetcher import DataFetcher

# Third-party packages


class GuessitAPI(DataFetcher):
    def __init__(self, name=None):
        super().__init__(name)

    def fetch_data(self, **kwargs):
        if 'filename' in kwargs.keys():
            filename = kwargs.get('filename')
            guessit_data = guessit(filename)
        else:
            raise ValueError("")

        return dict(guessit_data)

    def get_optional_params(self):
        return None

    def get_required_params(self):
        return ['filename']
