# Standard Python imports
import argparse
import math
import re
import sys
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
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import scipy as sp

# Docs
# https://pytube.io/en/latest/index.html
# https://www.omdbapi.com/
# https://api.movieposterdb.com/docs/#docs/documentation/
# https://guessit.readthedocs.io/en/latest/

# TODO: Implement http://www.opensubtitles.org/en API
# https://opensubtitles.stoplight.io/docs/opensubtitles-api/e3750fd63a100-getting-started
# There exists python-opensubtitles

# TODO: Modularize implementation with a package structure
#       Consider local data management/ API / dataframe

from constants import *


class RateLimitExceededError(Exception):
    def __init__(self):
        super().__init__("Rate limit exceeded.")


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
    # Rate limit is 1000 calls/day
    # TODO: Implement rate limit
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

    if response.status_code == 429:
        # TODO: Implement unit test
        logging.error('Rate limit exceeded. Status code {}'.format(response.json()['Error']))
        raise RateLimitExceededError()

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


class CollectionDataframe:
    def __init__(self, collection: dict=None):
        # Convert the nested data to a DataFrame
        # Create an empty DataFrame
        self.df = pd.DataFrame()
        if collection is None:
            logging.warning(
                'Collection dataframe was created, but no metadata was passed to the constructor. No metadata'
                'loaded.')
        else:
            self.load(collection)

    def filter(self, col, val, comp=None):
        if comp not in ('<', '>', None):
            raise ValueError("Optional comparator must be either '<' or '>'.")

        # This method of extracting numeric values of strings is tolerant of
        # ranges and unicode characters which are often present in OMDB data.
        # Another method would be to use
        #
        # self.df = self.df[self.df[col].apply(pd.to_numeric, errors='coerce') < val]
        #
        # However, that results in lost entries.
        if isinstance(val, (int, float)):
            if comp == '<':
                # .extract() uses a regex to get the first number out of every entry in the column,
                # returns a dataframe, and .squeeze() turns it back into a column.
                # .to_numeric() turns out extracted stings into floats, wile errors='coerce' ignores
                # problems that otherwise arise from things like unicode characters.
                extract_num = self.df[col].str.extract('(\d+)').squeeze()
                str_to_float = pd.to_numeric(extract_num, errors='coerce')
                self.df = self.df[str_to_float < val]
            elif comp == '>':
                extract_num = self.df[col].str.extract('(\d+)').squeeze()
                str_to_float = pd.to_numeric(extract_num, errors='coerce')
                self.df = self.df[str_to_float > val]
            else:
                raise ValueError("Comparator must be specified for numeric values.")

        elif isinstance(val, str):
            if comp == '<':
                self.df = self.df[self.df[col].str.lower() < str(val).lower()]
            elif comp == '>':
                self.df = self.df[self.df[col].str.lower() > str(val).lower()]
            else:
                self.df = self.df[self.df[col].str.contains(str(val), case=False, na=False)]
        else:
            raise TypeError("Unsupported filter value type. Must be STR, INT, or FLOAT.")

        if comp is None:
            if isinstance(val, (str, int, float)):
                self.df = self.df[self.df[col].str.contains(str(val), case=False, na=False)]
            else:
                raise TypeError("Unsupported filter value type. Must be STR, INT, or FLOAT.")

    def sort(self, col):
        if self.df is None:
            raise ValueError(f"No dataframe is currently loaded, or it is empty. ")
        elif col not in self.df.columns:
            raise ValueError(f"Column {col} not in the current dataframe")
        else:
            self.df = self.df.sort_values(by=col)

    def load(self, collection):
        # This procedure prevents each column from being prefixed with the lengthy sha256 hash
        # Extract hashes and nested data into separate lists
        hashes = list(collection.keys())
        nested_data = list(collection.values())

        # Create a "Video Hash" column
        self.df["Video Hash"] = hashes

        # Flatten the nested data into columns and put it to the right of the hash column
        self.df = pd.concat([self.df, pd.json_normalize(nested_data)], axis=1)

        pd.set_option('display.max_columns', None)

    def generate_m3u_playlist(self):
        path = './playlist_example.m3u'
        playlist = ''
        for _, row in self.df.iterrows():
            root = row['file_data.root']
            filename = row['file_data.filename']
            playlist += os.path.join(root, filename) + '\n'

        with open(path, 'w', encoding='utf-8') as file:
            file.write(playlist)

    def generate_graph(self):
        # Generates a graph associating movies by actors and directors
        g = nx.Graph()
        nodes = []
        for index, row in self.df.iterrows():
            title = row['omdb_data.Title']
            if title not in nodes:
                nodes.append(title)                                     # add movie to node list
                g.add_node(title, type="Movie")                         # create movie node
                if type(row['omdb_data.Actors']) is str:
                    actors = row['omdb_data.Actors'].split(',')
                    for actor in actors:                                # for each actor in movie
                        if actor not in nodes:                          # if actor not in list
                            nodes.append(actor)                         # add actors to node list
                            g.add_node(actor, type="Actor")             # create actor node
                        g.add_edge(title, actor)                        # add edge from movie to actor
                if type(row['omdb_data.Director']) is str:
                    directors = row['omdb_data.Director'].split(',')
                    for director in directors:                          # for each director in movie
                        if director not in nodes:                       # if director not in node list
                            nodes.append(director)                      # add director to node list
                            g.add_node(director, type="Director")       # create director node
                        g.add_edge(title, director)                     # add edge from movie to director
        return g

    def trim_unrelated(self, g: nx.Graph):
        # actor_nodes = nx.get_node_attributes(g, 'Actor')
        # print(actor_nodes)
        self.display_graph(g)
        trim = []
        for node, data in g.nodes.data():
            if (data.get('type') == 'Actor') and (g.degree(node) < 2):
                trim.append(node)
            if (data.get('type') == 'Director') and (g.degree(node) < 2):
                trim.append(node)
        for node in trim:
            g.remove_node(node)
        trim.clear()
        for node, data in g.nodes.data():
            print("{}: {}".format(node, g.degree(node)))
            if (data.get('type') == 'Movie') and (g.degree(node) == 0):
                trim.append(node)
        for node in trim:
            g.remove_node(node)
        self.display_graph(g)

    def display_graph(self, g):
        node_colors = []
        for n in g.nodes:
            node_type = g.nodes[n]['type']
            if node_type == 'Actor':
                node_colors.append('lightblue')
            elif node_type == 'Director':
                node_colors.append('lightgreen')
            elif node_type == 'Movie':
                node_colors.append('lightcoral')
            else:
                node_colors.append('gray')  # Default color for unknown types

        plt.figure(figsize=(50, 50))
        pos = nx.spring_layout(g, k=None)  # Okayish
        # pos = nx.arf_layout(g) # Evenly space, generally okay
        # pos = nx.shell_layout(g) # Terrible, just circular
        # pos = nx.circular_layout(g, scale=1, dim=1)  # Position nodes
        # pos = nx.planar_layout(g) # took too long to render
        # pos = nx.spectral_layout(g, weight=1, scale=0.01, center=(0,0), dim=2) # Promising, but spacing needs to be worked out
        # pos = nx.kamada_kawai_layout(g)
        pos = nx.fruchterman_reingold_layout(g, k=25/math.sqrt(g.number_of_nodes()), iterations=1000)
        nx.draw(g, pos, with_labels=True, node_color=node_colors, node_size=5000, font_size=10, width=1.5)
        plt.show()

    def display_graph_plotly(self, G):
        pos = nx.fruchterman_reingold_layout(G, k=0.750, iterations=500)
        fig = go.Figure(go.Scatter(x=[], y=[], mode='markers', hoverinfo='text'))

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            fig.add_trace(
                go.Scatter(x=[x0, x1, None], y=[y0, y1, None], mode='lines', line=dict(width=0.5, color='#888')))

        for node in G.nodes():
            x, y = pos[node]
            fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', hovertext=f'Node {node}', marker=dict(size=10)))

        # Update layout for better presentation
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
        )

        # Show the plot
        fig.show()

    def __repr__(self):
        return self.df.__repr__()


if __name__ == "__main__":
    load_dotenv('./config.env')
    source = os.getenv('SOURCE_PATH')
    dest = os.getenv('DEST_PATH')

    init_logger()

    # collection = {}
    # scan_directory(collection, 'C:\\Users\\User\\Videos\\Misc Media')
    # save_metadata(collection)

    data = load_metadata()
    df = CollectionDataframe(data)
    # # df.sort('omdb_data.Year')
    # df.filter('omdb_data.Year', 1986, '>')
    # df.filter('omdb_data.Year', 1990, '<')
    # df.df.to_html("flat_test.html", index=False)

    # df.generate_m3u_playlist()

    g = df.generate_graph()
    df.trim_unrelated(g)
    # df.display_graph_plotly(g)
