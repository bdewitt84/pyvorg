# source/api/omdb_api.py

# Standard library
import os
import logging

# Local imports
from source.constants import *
from source.api.api_interface import APIInterface

# Third-party packages
import requests


class OMDBAPI(APIInterface):
    def __init__(self):
        super().__init__()
        self.api_url = 'https://www.omdbapi.com'
        self.api_key = os.getenv(ENV_OMDB_KEY)

    def fetch_video_data(self, title, **kwargs):
        """ TODO: Update docstring
            Fetches movie videos from the OMDB API based on the provided title.

            This function makes an HTTP GET request to the OMDB API using the specified movie title
            as a query parameter. It uses the API key retrieved from the environment variable 'OMDB_KEY'
            and constructs the request URL. If the request is successful and the API response indicates
            success, the retrieved movie videos is returned. Otherwise, warning messages are logged.

            Args:
                title (str): The title of the movie for which to retrieve videos.

            Returns:
                dict or None: A dictionary containing movie videos if the request is successful,
                              or None if there was an error.
        """

        if not self.api_key:
            raise ValueError(f"No API key set. Add '{ENV_OMDB_KEY} = [your omdb key]' to {ENV_FILE_PATH}.")
        params = {
            'apikey': self.api_key,
            't': title
        }

        if 'year' in kwargs:
            params['y'] = kwargs.get('year')

        if 'plot' in kwargs:
            val = kwargs.get('plot')
            if val == 'full':
                params['plot'] = val
            elif val == 'short':
                # OMDB defaults to short
                pass
            else:
                raise ValueError(f"'{val}' is not a valid parameter for 'plot'. Valid parameters are 'full' or 'short'")

        val = kwargs.get('rtype')
        if val in ['json', 'xml']:
            params['r'] = val
        elif val is None:
            # OMDB defaults to JSON
            pass
        else:
            raise ValueError(f"'{val}' is not a valid parameter for 'rtype'. Valid parameters are 'json' or 'xml'")

        response = requests.get(self.api_url, params=params)

        data = None

        # Handle specific status codes
        if response.status_code == 200:
            if response.json()['Response'] == 'True':
                data = response.json()
            else:
                logging.warning(f"Error requesting OMDB videos for '{title}': {response.json()['Error']}")

        elif response.status_code == 429:
            msg = f"Status code {response.json()['Error']}: Rate limit exceeded."
            logging.error(msg)
            raise requests.HTTPError(msg)

        # Handle unspecified status codes
        elif 400 <= response.status_code <= 499:
            msg = f"Status code {response.json()['Error']}: Undefined client error"
            logging.error(msg)
            raise requests.HTTPError(msg)

        elif 500 <= response.status_code <= 599:
            msg = f"Status code {response.json()['Error']}: Undefined server error"
            logging.error(msg)
            raise requests.HTTPError(msg)

        else:
            msg = f"Status code {response.status_code}: Undefined error"
            logging.error(msg)
            raise requests.HTTPError(msg)

        return data
