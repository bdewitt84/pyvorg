# Standard Python imports
import argparse
import tempfile
import jsonschema

import colorlog as colorlog
from datetime import datetime
import json
import logging
import os

import pytube.exceptions
import requests as requests
import shutil

# Additional imports
import pandas as pd
from dotenv import load_dotenv
import guessit
import hashlib
from pytube import YouTube, Search
from tqdm import tqdm

# Docs
# https://pytube.io/en/latest/index.html
# https://www.omdbapi.com/
# https://api.movieposterdb.com/docs/#docs/documentation/
# https://guessit.readthedocs.io/en/latest/

# TODO: Implement http://www.opensubtitles.org/en API
# https://opensubtitles.stoplight.io/docs/opensubtitles-api/e3750fd63a100-getting-started
# There exists python-opensubtitles

from constants import *


# TODO: Refactor all of the functions to process the collection dict along with the video id.


def handle_file_exceptions(func):
    """
    Decorator to handle common file-related exceptions.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        # Assuming the path argument is present in *args
        path = args[func.__code__.co_varnames.index('path')]
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file '{path}' does not exist.")
            return func(*args, **kwargs)
        except PermissionError:
            raise PermissionError(f"Permission denied while accessing '{path}'.")

    return wrapper


# @handle_file_exceptions
def hash_sha256(path):
    """
    Compute the SHA-256 hash of a file located at the given path.

    This function reads the content of the specified file in chunks and
    computes the SHA-256 hash of its contents.

    Args:
        path (str): The path to the file for which to compute the hash.

    Returns:
        str: The computed SHA-256 hash in hexadecimal format.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If there's a permission issue while reading the file.
    """
    hasher = hashlib.sha256()
    file_size = os.path.getsize(path)

    with open(path, 'rb') as file:
        chunk_size = 65536  # 64kb
        with tqdm(total=file_size, unit='MB', unit_scale=True, position=0) as progress_bar:
            max_desc_width = 80 - len(' [Hashing]')
            file_name = os.path.basename(path)
            file_name = file_name[:max_desc_width].ljust(max_desc_width)
            progress_bar.set_description(f'[Hashing] {file_name}')
            for chunk in iter(lambda: file.read(chunk_size), b''):
                hasher.update(chunk)
                progress_bar.update(len(chunk))
    hash = hasher.hexdigest()
    return hash


# @handle_file_exceptions
def add_video(collection, path):
    """
    Add video information to the collection based on the specified path.

    This function takes a collection of video data and a file path,
    computes the SHA-256 hash of the file at the given path, and adds
    relevant information about the video to the collection.

    Args:
        collection (dict): A dictionary representing the collection of video data.
        path (str): The full path to the video file to be added to the collection.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If there's a permission issue while reading the file.
    """
    root, file = os.path.split(path)
    video_id = hash_sha256(path)
    timestamp = generate_timestamp()
    local_data = {FILENAME: file, ROOT: root, TIMESTAMP: timestamp}
    video = {FILE_DATA: local_data}
    collection.update({video_id: video})


def scan_directory(collection, path):
    """
    Recursively scans a directory for video files and adds them to the collection.

    This function traverses the specified directory and its subdirectories, identifying
    video files based on a predefined list of video extensions. For each video file found,
    it constructs the full path and invokes the 'add_video' function to add the video's
    information to the provided collection.

    Args:
        collection (dict): A dictionary representing the collection of video information.
                           Videos will be added to this collection.
        path (str): The path of the directory to scan for video files.

    Returns:
        None
    """

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(VIDEO_EXTENSIONS):
                file_path = os.path.join(root, file)
                add_video(collection, file_path)


def guess_title(video):
    """
    Guesses the title of a video based on its filename.

    This function uses the 'guessit' library to analyze the filename of a video and
    extract a guessed title from it. The function assumes that the video information
    is structured within the 'video' dictionary, and the filename is stored in the
    'FILE_DATA' subdictionary under the 'FILENAME' key.

    Args:
        video (dict): A dictionary containing information about the video, typically
                      obtained from the video collection. It should have the 'FILE_DATA'
                      subdictionary containing the filename under the 'FILENAME' key.

    Returns:
        str: The guessed title of the video based on its filename.
    """
    return guessit.guessit(video[FILE_DATA][FILENAME])['title']
    # return guessit.guessit(video[FILE_DATA][FILENAME])


def update_omdb_data(video):
    """
    Updates the video dictionary with movie data from the OMDB API.

    This function retrieves movie data for the video's guessed title from the OMDB API
    using the 'get_omdb_data' function, and if successful, updates the provided video
    dictionary with the retrieved data under the 'OMDB_DATA' key.

    Args:
        video (dict): The video dictionary to update with OMDB data. The dictionary should
                      contain information about the video, typically obtained from the
                      video collection.

    Returns:
        None
    """
    guess = guess_title(video)

    data = get_omdb_data(guess)

    if data:
        video.update({OMDB_DATA: data})
        logging.info(f'OMDB data for {video[FILE_DATA][FILENAME]} updated successfully')
    else:
        video.update({OMDB_DATA: f'OMDB search for \"{guess}\" returned no results.'})


def get_omdb_data(title):
    """
        Fetches movie data from the OMDB API based on the provided title.

        This function makes an HTTP GET request to the OMDB API using the specified movie title
        as a query parameter. It uses the API key retrieved from the environment variable 'OMDB_KEY'
        and constructs the request URL. If the request is successful and the API response indicates
        success, the retrieved movie data is returned. Otherwise, warning messages are logged.

        Args:
            title (str): The title of the movie for which to retrieve data.

        Returns:
            dict or None: A dictionary containing movie data if the request is successful,
                          or None if there was an error.
    """
    api_url = 'https://www.omdbapi.com'

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
            logging.warning(f'Error requesting OMDB data for title {title}: ' + response.json()['Error'])
    else:
        logging.warning('Error processing request. Status code {}'.format(response.status_code))

    return data


def save_metadata(collection, path='./'):
    """
    Save a collection of metadata to a JSON file.

    This function takes a collection of metadata and writes it to a JSON file
    specified by the 'path' parameter. The metadata is serialized as JSON data
    with an optional indentation of 4 spaces.

    Args:
        collection (dict): A dictionary containing metadata to be saved.
        path (str, optional): The path to the output JSON file. Defaults to './metadata.json'.

    Returns:
        None
    """
    path = os.path.join(path, 'metadata.json')
    with open(path, 'w') as file:
        json.dump(collection, file, indent=4)


def load_metadata(path='./metadata.json'):
    """
        Load metadata from a JSON file.

        Args:
            path (str, optional): The path to the JSON file containing metadata.
                Defaults to './metadata.json' if not provided.

        Returns:
            dict: A dictionary containing the loaded metadata.

        Raises:
            FileNotFoundError: If the specified JSON file does not exist.

        Example:
            metadata = load_metadata('path/to/metadata.json')
    """
    with open(path, 'r') as file:
        collection = json.load(file)
    return collection


def validate_metadata(collection):
    def validate_metadata(collection):
        """
        Validate metadata collection against a JSON Schema.

        Args:
            collection (dict): A dictionary containing metadata to be validated.

        Returns:
            bool: True if the metadata collection is valid according to the schema, False otherwise.

        Notes:
            This function uses JSON Schema validation to check if the provided metadata
            adheres to the specified schema.

        Example:
            metadata = {
                "title": "Example Metadata",
                "description": "A sample metadata collection.",
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ]
            }
            is_valid = validate_metadata(metadata)
            if is_valid:
                print("Metadata is valid.")
            else:
                print("Metadata validation failed.")
        """

    schema = METADATA_SCHEMA
    valid = True

    try:
        jsonschema.validate(collection, schema)
    except jsonschema.exceptions.ValidationError as error:
        valid = False
        message = 'Metadata validation failed at {}:\n {}'.format(
            list(error.path),
            error.message
        )
        logging.warning(message)

    return valid


def merge_metadata(collection1, collection2):
    # TODO: this might be useful at some point -- PYTHON can merge dicts in one line
    for id in collection1:
        # if id is in videos2,
        #   compare timestamps, keep the most recent
        # else
        #   just update it
        pass


def generate_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def validate_timestamp(timestamp):
    valid = True
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        valid = False
    return valid


def init_logger():
    logging.basicConfig(filename='./applog.txt',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(asctime)s - %(log_color)s%(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_yellow',
        },
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)


def find_trailer(video, num_results=1):
    title = video[OMDB_DATA][TITLE]
    search = Search(title + ' official trailer')

    trailer_urls = []
    for result in range(num_results):
        trailer_id = search.results[result].video_id
        trailer_url = 'https://www.youtube.com/watch?v=' + trailer_id
        trailer_urls.append(trailer_url)

    return trailer_urls


def download_trailer(path, youtube_url):
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


def verify_video(video):
    # TODO: Change to verify_file_data(), separate responsibilities from verify_metadata()
    path = os.path.join(video[FILE_DATA][ROOT], video[FILE_DATA][FILENAME])
    verified = False
    if os.path.exists(path):
        verified = True
        logging.info('passed validation: {}'.format(path))
    else:
        logging.warning('failed validation: {}'.format(path))
    return verified


def remove_empty_dir(path):
    removed = False
    if os.listdir(path) == 0:
        os.rmdir(path)
        logging.info('Removed empty directory {}'.format(path))
        removed = True
    else:
        logging.warning('Directory not empty {}'.format(path))
    return removed


def generate_video_dir(video, path):
    if OMDB_DATA in video and video[OMDB_DATA] is not None:
        new_dir = os.path.join(path, video[OMDB_DATA][TITLE])
    else:
        new_dir = os.path.join(path, 'unidentified')
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        logging.info('Created directory {}'.format(new_dir))
    else:
        logging.info('Directory already exists {}'.format(new_dir))
    return new_dir


def place_video(video, path):
    current_path = os.path.join(video[FILE_DATA][ROOT], video[FILE_DATA][FILENAME])
    shutil.move(current_path, path)
    video[FILE_DATA].update({ROOT: path})
    logging.info('Moved {} \n to {}'.format(current_path, path))


def organize_collection(collection, path, rem_empty=False):
    for video in collection:
        if verify_video(video):
            generate_video_dir(video, path)
            place_video(video, path)
            if rem_empty:
                remove_empty_dir(path)


if __name__ == "__main__":
    load_dotenv('./config.env')
    source = os.getenv('SOURCE_PATH')
    dest = os.getenv('DEST_PATH')

    init_logger()

    # collection = {}
    # scan_directory(collection, 'C:\\Users\\User\\Videos\\Misc Media')
    # save_metadata(collection)

    data = load_metadata()
    # Convert the nested data to a DataFrame
    # Create an empty DataFrame
    result_df = pd.DataFrame()

    # Extract hashes and nested data into separate lists
    hashes = list(data.keys())
    nested_data = list(data.values())

    # Create a "Video Hash" column
    result_df["Video Hash"] = hashes

    # Flatten the nested data into columns
    result_df = pd.concat([result_df, pd.json_normalize(nested_data)], axis=1)

    pd.set_option('display.max_columns', None)

    # Print the result DataFrame
    print(result_df)
