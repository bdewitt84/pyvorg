# source/api.py

"""
    This module handles API interactions from sources such as OMDB and YouTube, among others.
"""

# Standard imports
import logging
import os

# local imports
from source.constants import *
from source.exceptions import RateLimitExceededError

# Third party imports
from pytube import YouTube, Search
import requests

# Docs
# https://pytube.io/en/latest/index.html
# https://www.omdbapi.com/


def get_omdb_data(title):
    """
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
    # Rate limit is 1000 calls/day
    # TODO: Implement rate limit
    api_url = 'https://www.omdbapi.com'

    # TODO: verify API key

    params = {
        'apikey': os.getenv('OMDB_KEY'),
        't': title
    }

    response = requests.get(api_url, params=params)

    data = None
    if response.status_code == 200:
        if response.json()['Response'] == 'True':
            data = response.json()
        else:
            logging.warning(f'Error requesting OMDB videos for title {title}: ' + response.json()['Error'])

    elif response.status_code == 429:
        # TODO: Implement unit test
        logging.error('Rate limit exceeded. Status code {}'.format(response.json()['Error']))
        raise RateLimitExceededError()

    else:
        logging.warning('Error processing request. Status code {}'.format(response.status_code))

    return data


def trailer_download(path, youtube_url):
    yt = YouTube(youtube_url)
    title = yt.title
    full_trailer_path = os.path.join(path, yt.title)

    if not os.path.exists(full_trailer_path):
        video_stream = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()
        if video_stream:
            filename = title + '.mp4'
            video_stream.download(output_path=path, filename=filename)
            print(filename + ' saved to ' + path)
        else:
            logging.error('No suitable video stream could be found.')
    else:
        logging.error(full_trailer_path + ' already exists.')


def trailer_find(video, num_results=1):
    title = video[OMDB_DATA][OMDB_TITLE]
    search = Search(title + ' official trailer')

    trailer_urls = []
    for result in range(num_results):
        trailer_id = search.results[result].video_id
        trailer_url = 'https://www.youtube.com/watch?v=' + trailer_id
        trailer_urls.append(trailer_url)

    return trailer_urls
