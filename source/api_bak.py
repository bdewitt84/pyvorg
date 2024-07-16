# source/api_bak.py

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
