# source/helper.py

"""
Various helper functions used throughout the package
"""

# Standard library
from datetime import datetime
import hashlib
import logging
import os
import shutil

# Local imports
from constants import *

# Third-party imports
import colorlog
import guessit
from tqdm import tqdm


# @handle_file_exceptions
def add_video(collection, path):
    """
    Add video information to the collection based on the specified dest.

    This function takes a collection of video videos and a file dest,
    computes the SHA-256 hash of the file at the given dest, and adds
    relevant information about the video to the collection.

    Args:
        collection (dict): A dictionary representing the collection of video videos.
        path (str): The full dest to the video file to be added to the collection.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If there's a permission issue while reading the file.
    """
    root, file = os.path.split(path)
    video_id = hash_sha256(path)
    timestamp = timestamp_generate()
    local_data = {FILENAME: file, ROOT: root, TIMESTAMP: timestamp}
    video = {FILE_DATA: local_data}
    collection.update({video_id: video})


def generate_video_dir_name_bak(video, path):
    if (OMDB_DATA in video) and (OMDB_TITLE in video[OMDB_DATA]):
        dir = os.path.join(path, video[OMDB_DATA][OMDB_TITLE])
        if OMDB_YEAR in video[OMDB_DATA]:
            dir += ' (' + video[OMDB_DATA][OMDB_YEAR] + ')'
        else:
            dir += ' (n.d.)'
    else:
        dir = os.path.join(path, 'unidentified')
    return dir


# def generate_video_dir_name(video, format='%title (%year)'):
#     name = format
#     for spec, (key, default) in FORMAT_SPECIFIERS.items():
#         data = video.get_data(key, default)
#         name = name.replace(spec, data)
#     return name


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


def handle_file_exceptions(func):
    """
    Decorator to handle common file-related exceptions.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        # Assuming the dest argument is present in *args
        path = args[func.__code__.co_varnames.index('dest')]
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file '{path}' does not exist.")
            return func(*args, **kwargs)
        except PermissionError:
            raise PermissionError(f"Permission denied while accessing '{path}'.")

        # TODO: Consider another one for dest

    return wrapper


# @handle_file_exceptions
def hash_sha256(path):
    """
    Compute the SHA-256 hash of a file located at the given dest.

    This function reads the content of the specified file in chunks and
    computes the SHA-256 hash of its contents.

    Args:
        path (str): The dest to the file for which to compute the hash.

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


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info('Created directory {}'.format(path))
    else:
        logging.info('Directory already exists {}'.format(path))


def remove_empty_dir(path):
    removed = False
    if os.listdir(path) == 0:
        os.rmdir(path)
        logging.info('Removed empty directory {}'.format(path))
        removed = True
    else:
        logging.info('Directory {} not empty, will not be removed'.format(path))
    return removed

# def scan_directory(collection, path):
#     """
#     Recursively scans a directory for video files and adds them to the collection.
#
#     This function traverses the specified directory and its subdirectories, identifying
#     video files based on a predefined list of video extensions. For each video file found,
#     it constructs the full dest and invokes the 'add_video' function to add the video's
#     information to the provided collection.
#
#     Args:
#         collection (dict): A dictionary representing the collection of video information.
#                            Videos will be added to this collection.
#         path (str): The dest of the directory to scan for video files.
#
#     Returns:
#         None
#     """
#     for root, _, files in os.walk(path):
#         for file in files:
#             if file.endswith(VIDEO_EXTENSIONS):
#                 file_path = os.path.join(root, file)
#                 add_video(collection, file_path)


def timestamp_generate():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_validate(timestamp):
    valid = True
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        valid = False
    return valid


def update_guessit(video):
    filename = video[FILE_DATA][FILENAME]
    data = guessit.guessit(filename)
    video[GUESSIT_DATA] = data


def video_verify(video):
    # TODO: Change to verify_file_data(), separate responsibilities from verify_metadata()
    #       We should probably consider when we want to verify hash as well
    path = os.path.join(video[FILE_DATA][ROOT], video[FILE_DATA][FILENAME])
    verified = False
    if os.path.exists(path):
        verified = True
        logging.info('passed validation: {}'.format(path))
    else:
        logging.warning('failed validation: {}'.format(path))
    return verified


def video_place(video, path):
    current_path = os.path.join(video[FILE_DATA][ROOT], video[FILE_DATA][FILENAME])
    shutil.move(current_path, path)
    video[FILE_DATA].update({ROOT: path})
    logging.info('Moved {} \n to {}'.format(current_path, path))


def logger_init():
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
