# source/api/guessit_api.py

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
from source.api.base_api import BaseAPI

# Third-party packages


class GuessitAPI(BaseAPI):
    def __init__(self, name='guessit'):
        super().__init__(name)

    def fetch_video_data(self, **kwargs):

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
