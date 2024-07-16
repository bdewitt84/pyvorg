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


def class_name(obj):
    return obj.__class__.__name__


def default_serializer(obj):
    return f"Object '{class_name(obj)}' is not serializable"


def file_write(path: str, data: str) -> None:
    """
    Attempts to write data to the file at the specified path, raising
    an exception if the file already exists.

    :param path: (str) Path to file.
    :param data: (str) Data to write to the file.
    :return : None
    :raises FileExistsError: if the file already exists
    :raises IOError: if an error occurs with the write function
    """
    if os.path.exists(path):
        raise FileExistsError(f"The file '{path}' already exists.")
    with open(path, 'w') as file:
        file.write(data)


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


def logger_init():
    current_path = os.path.dirname(__file__)
    log_path = os.path.join(current_path, '..', 'logs', 'applog.txt')
    logging.basicConfig(
        filename=log_path,
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


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Directory '{path}' created")
    else:
        logging.info(f"Directory '{path}' already exists")


def move_file(src, dst, overwrite=False):
    if os.path.exists(dst) and not overwrite:
        msg = f"Cannot move file: '{dst}' already exists"
        logging.error(msg)
        raise FileExistsError(msg)
    elif os.path.exists(dst) and overwrite:
        logging.info(f"Overwriting '{dst}' with '{src}'")
    else:
        logging.info(f"Moved '{src}' to '{dst}'")
    shutil.move(src, dst)


def remove_empty_dir(path):
    removed = False
    if os.listdir(path) == 0:
        os.rmdir(path)
        logging.info('Removed empty directory {}'.format(path))
        removed = True
    else:
        logging.info('Directory {} not empty, will not be removed'.format(path))
    return removed


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
    print(data)
