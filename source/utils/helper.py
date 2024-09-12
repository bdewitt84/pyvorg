# source/helper.py

"""
    Various helper functions used throughout the package
"""

# Standard library
from datetime import datetime
import logging
from pathlib import Path
from typing import Callable

# Local imports
from source.datafetchers.base_fetcher import DataFetcher
from source.constants import DATA_PREF_ORDER

# Third-party imports
import colorlog


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


def find_missing_params(required_params: list[str], params: dict):
    return [key for key in required_params if params.get(key) is None]


def get_preferred_sources() -> list[str]:
    return DATA_PREF_ORDER


def logger_init(path):
    log_path = path / 'logs.txt'
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


def timestamp_generate():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_validate(timestamp):
    valid = True
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        valid = False
    return valid


def update_api_data(video, api: DataFetcher, **kwargs) -> None:
    required_params = api.get_required_params()
    if missing := find_missing_params(required_params, kwargs):
        raise ValueError(f"Parameters {missing} were not supplied and could not be retrieved from '{video}' metadata")
    data = api.fetch_data(**kwargs)
    video.set_source_data(api.get_name(), data)
