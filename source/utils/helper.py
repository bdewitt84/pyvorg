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


def class_name(obj):
    return obj.__class__.__name__


def create_dummy_videos(path, n):
    """
    Creates n dummy videos at directory 'path'
    :param path: Directory where dummy videos will be created
    :param n: number of dummy videos to create
    :returns: list of videos
    """
    videos = []
    for i in range(n):
        filename = 'test_video_' + str(i) + '.mp4'
        filepath = os.path.join(path, filename)
        with open(filepath, 'w') as file:
            file.write(str(i))
        videos.append(filepath)
    return videos


def default_serializer(obj):
    return f"Object '{class_name(obj)}' is not serializable"


def file_write(path: str, data: str, overwrite=False) -> None:
    """
    Attempts to write data to the file at the specified path, raising
    an exception if the file already exists.

    :param path: (str) Path to file.
    :param data: (str) Data to write to the file.
    :param overwrite: (bool) Overwrite if file exists
    :return : None
    :raises FileExistsError: if the file already exists
    :raises IOError: if an error occurs with the write function
    """
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"The file '{path}' already exists.")
    with open(path, 'w') as file:
        file.write(data)


def file_read(path: str) -> str:
    """
    :param path:
    :return:
    """
    with open(path, 'r') as file:
        return file.read()


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
    sha256_hash = hasher.hexdigest()
    return sha256_hash


def integer_generator():
    num = 0
    while True:
        yield num
        num += 1


def logger_init():
    current_path = os.path.dirname(__file__)
    log_path = os.path.join(current_path, '..', '..', 'logs', 'applog.txt')
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


def mimic_folder(src, dest):
    gen = integer_generator()
    for dirpath, _, filenames in os.walk(src):
        for name in filenames:
            src_path = os.path.join(dirpath, name)
            relative_to_src = dirpath[len(src) + 1:]
            file_path = os.path.join(dest, relative_to_src, name)
            new_dir = os.path.join(dest, relative_to_src)
            os.makedirs(new_dir, exist_ok=True)
            print('Creating dummy of ' + src_path + ' at\n' + file_path)
            data = str(next(gen))
            file_write(file_path, data)


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
