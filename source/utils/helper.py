# source/helper.py

"""
    Various helper functions used throughout the package
"""

# Standard library
from datetime import datetime
import hashlib
import logging
import os
from pathlib import Path
import platform
import shutil
from typing import Callable

# Local imports
from constants import APP_NAME

# Third-party imports
import colorlog
from tqdm import tqdm


def class_name(obj):
    return obj.__class__.__name__


def create_dummy_files(path: Path, n, func: Callable = lambda x: 'dummy_file_' + str(x) + '.file'):
    """
    Creates n dummy videos at directory 'path'
    :param func: Function that takes an int and returns a string
    :param path: Directory where dummy videos will be created
    :param n: number of dummy videos to create
    :returns: list of videos
    """
    file_paths = []
    for i in range(n):
        filename = func(i)
        file_path = Path(path) / filename
        with file_path.open('w') as file:
            file.write(str(i))
        file_paths.append(file_path)
    return file_paths


def default_serializer(obj):
    return f"Object '{class_name(obj)}' is not serializable"


def file_write(path: Path, data: str, overwrite=False) -> None:
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
    if path.exists() and not overwrite:
        raise FileExistsError(f"The file '{path}' already exists")
    with path.open('w') as file:
        file.write(data)


def file_read(path: Path) -> str:
    """
    Reads data from file at 'path'
    :param path: Path of file to be read
    :return: string containing file data
    """
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' cannot be found")
    with path.open('r') as file:
        return file.read()


def generate_destination_paths(videos, dst_tree: Path = None):
    # TODO: Consider making this MoveCommand's responsibility
    if dst_tree is None:
        dst_tree = Path(get_default_dst_tree())
        return [dst_tree / video.generate_dir_name() for video in videos]


def get_default_dst_tree():
    return os.getenv(ENV_DEST_PATH)


def get_files_from_path(root: Path, recursive: bool = False, glob_pattern: str = '*') -> list[Path]:
    if recursive:
        return list(root.rglob(glob_pattern))
    else:
        return list(root.glob(glob_pattern))


def get_file_type(path: Path) -> str:
    if not path.is_file():
        raise TypeError(f"'{path}' is not recognized as a valid file")
    if path.suffix in VIDEO_EXTENSIONS:
        return 'video'
    else:
        return ''


def get_preferred_sources() -> list[str]:
    return DATA_PREF_ORDER


def get_user_cache_dir():
    system = platform.system()

    if system == 'Windows':
        return Path(os.getenv('APPDATA')) / 'local' / APP_NAME / 'Cache'


def get_user_config_dir():
    system = platform.system()

    if system == 'Windows':
        return Path(os.getenv('APPDATA')) / 'local' / APP_NAME / 'Config'


def get_user_exports_dir():
    system = platform.system()

    if system == 'Windows':
        return Path.home() / 'Documents' / APP_NAME / 'Export'


def get_user_profile_dir():
    system = platform.system()

    if system == 'Windows':
        return Path(os.getenv('APPDATA')) / 'local' / APP_NAME / 'Profiles'


def get_user_logs_dir():
    system = platform.system()

    if system == 'Windows':
        return Path(os.getenv('APPDATA')) / 'local' / APP_NAME / 'Logs'


def hash_sha256(path: Path):
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

    with path.open('rb') as file:
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
    # TODO: Use Path objects?
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


def make_dir(path: Path):
    if not path.exists():
        path.mkdir()
        logging.info(f"Directory '{path}' created")
    else:
        logging.info(f"Directory '{path}' already exists")


def mimic_folder(src_tree: Path, dest_tree: Path) -> None:
    gen = integer_generator()
    for dirpath, _, filenames in os.walk(src_tree):
        relative_to_src = Path(dirpath).relative_to(src_tree)
        Path(dest_tree, relative_to_src).mkdir(exist_ok=True)
        for name in filenames:
            dest_file_path = dest_tree / relative_to_src / name
            dummy_file_data = str(next(gen))
            file_write(dest_file_path, dummy_file_data, overwrite=False)


def move_file(src: Path, dst: Path, overwrite=False) -> None:
    if dst.exists():
        if not overwrite:
            msg = f"Cannot move file: '{dst}' already exists"
            logging.error(msg)
            raise FileExistsError(msg)
        logging.warning(f"Overwriting '{dst}' with '{src}'")
    shutil.move(src, dst)
    logging.info(f"Moved '{src}' to '{dst}'")


def parse_glob_string(path_string: str) -> (Path, str):
    path = Path(path_string)
    if '*' in path_string:
        return path.parent, path.name
    else:
        return path, '*'


def path_is_writable(path: Path) -> bool:
    return os.access(path, os.W_OK)


def path_is_readable(path: Path) -> bool:
    return os.access(path, os.R_OK)


def dir_is_empty(path: Path) -> bool:
    if not path.is_dir():
        raise NotADirectoryError("'path' must be a pathlib Path object that points to a directory")
    return not any(path.iterdir())


def timestamp_generate():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_validate(timestamp):
    valid = True
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        valid = False
    return valid
