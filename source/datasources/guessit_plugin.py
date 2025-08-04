# source/datasources/guessit_plugin.py

"""
    API interface for Guessit

    This module defines the GuessitAPI class, which provides methods for fetching video data
    from the Guessit, a python library that extracts as much information as possible from a
    video filename.

    Docs:
        https://guessit.readthedocs.io/en/latest/
"""


# Standard library
# n/a

# Local imports
from source.datasources.base_metadata_source import MetadataSource

# Third-party packages
from guessit import guessit


class GuessitAPI(MetadataSource):
    def __init__(self):
        super().__init__()

    def fetch_data(self, **kwargs):
        if 'filename' in kwargs.keys():
            filename = kwargs.get('filename')
            guessit_data = guessit(filename)
        else:
            raise ValueError("'filename', a required keyword, was not found in the argument dict'")

        return dict(guessit_data)

    def get_optional_params(self):
        return None

    def get_required_params(self):
        return ['filename']
