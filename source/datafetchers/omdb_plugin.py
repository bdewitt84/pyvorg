# source/datafetchers/omdb_plugin.py

"""
    API interface for OMDBFetcher (Open Movie Database)

    This module defines the OMDBFetcher class, which provides methods for fetching video data
    from the OMDBFetcher API.

    OMDBFetcher documentation:
        https://www.omdbapi.com/
"""

# Standard library
import os
import logging

# Local imports
from source.constants import *
from source.datafetchers.base_fetcher import DataFetcher

# Third-party packages
import requests

# OMDBFetcher parameter constants
P_TITLE = 't'
P_YEAR = 'y'
P_PLOT = 'plot'
P_API_KEY = 'apikey'
P_RETURN = 'r'

# Keyword argument constants
K_TITLE = 'title'
K_YEAR = 'year'
K_PLOT = 'plot'
K_RETURN = 'rtype'


class OMDBFetcher(DataFetcher):
    """
        A class to interact with the OMDBFetcher API.

        This class provides methods to fetch video data from the OMDBFetcher API based on various parameters
        such as title, year, plot type, and return format.
    """
    def __init__(self):
        """
            Initializes the OMDBFetcher class with the base URL and API key.

            Raises:
                ValueError: If the API key is not set in the environment variables.
        """
        super().__init__()
        # self.api_url = 'https://www.omdbapi.com'
        if not self.get_omdb_api_key():
            raise ValueError(f"No API key set. Add '{ENV_OMDB_KEY} = [your omdb key]' to {ENV_FILE_PATH}.")

    def fetch_data(self, **kwargs):
        """
            Fetches video data from the OMDBFetcher API based on provided parameters.

            This method constructs the appropriate query parameters and makes a request to the OMDBFetcher API.
            It handles the response and returns the video data if the request is successful.

            :param kwargs:
                **kwargs: Arbitrary keyword arguments including:
                    title (str): The title of the video. (required)
                    year (int): The release year of the video. (optional)
                    plot (str): The plot type, either 'short' or 'full'. Defaults to 'short'. (optional)
                    rtype (str): The return format, either 'json' or 'xml'. Defaults to 'json'. (optional)

            :returns:
                dict: The video data retrieved from the OMDBFetcher API.

            :raises:
                ValueError: If required parameters are missing or invalid.
                requests.HTTPError: If the request fails due to client or server errors.
        """

        params = self._construct_params(kwargs)
        data = self._query_omdb(params)

        return data

    @staticmethod
    def get_api_url():
        return 'https://www.omdbapi.com'

    @staticmethod
    def get_omdb_api_key():
        return os.getenv(ENV_OMDB_KEY)

    def get_optional_params(self):
        return [K_YEAR, K_PLOT, K_RETURN]

    def get_required_params(self):
        return [K_TITLE]

    def _construct_params(self, kwargs):
        """
            Constructs the query parameters for the OMDBFetcher API request
            :param kwargs:
                kwargs (dict): The keyword arguments for constructing query parameters.

            :returns:
                dict: The constructed query parameters.

            :raises:
                ValueError: If required parameters are missing or invalid.
        """
        params = {
            P_API_KEY: self.get_omdb_api_key(),
        }

        if K_TITLE in kwargs.keys():
            title = kwargs.get(K_TITLE)
            params[P_TITLE] = title
        else:
            raise ValueError(f"A title is required to query OMDBFetcher. Add '{K_TITLE}=[your title]' to the "
                             f"parameters of fetch_data(). Example: fetch_data({K_TITLE}='Alien')")

        if K_YEAR in kwargs.keys():
            params[P_YEAR] = kwargs.get(K_YEAR)

        if K_PLOT in kwargs:
            val = kwargs.get(P_PLOT)
            if val == 'full':
                params[P_PLOT] = val
            elif val == 'short':
                # OMDBFetcher defaults to short, so we just omit parameter 'plot'. In fact, I'm not sure 'short' is even
                # a valid value for this parameter.
                pass
            else:
                raise ValueError(f"'{val}' is not a valid parameter for '{K_PLOT}'. Valid parameters are 'full' or "
                                 f"'short'")

        val = kwargs.get(K_RETURN)
        if val in ['json', 'xml']:
            params[P_RETURN] = val
        elif val is None:
            # OMDBFetcher defaults to JSON, so we just omit parameter 'r'.
            pass
        else:
            raise ValueError(f"'{val}' is not a valid parameter for '{K_RETURN}'. Valid parameters are 'json' or 'xml'")

        return params

    def _query_omdb(self, params):
        """
            Makes a request to the OMDBFetcher API and handles the response
            :param params:
                params (dict): The query parameters for the OMDBFetcher API request.

            :returns:
                dict: The video data retrieved from the OMDBFetcher API.

            :raises:
                requests.HTTPError: If the request fails due to client or server errors.
        """
        response = requests.get(self.get_api_url(), params=params)

        title = params.get(P_TITLE)

        # Handle specific status codes
        if response.status_code == 200:
            data = response.json()
            if response.json()['Response'] == 'True':
                logging.info(f"OMDBFetcher data retrieved for '{title}'")
            else:
                logging.warning(f"Error requesting OMDBFetcher videos for '{title}': {response.json()['Error']}")

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
