# source.col.py

"""
    Collection class handles the main functionality of the package, including
    scanning for files, updating the metadata from online sources, and organizing
    the video files into a predefined file structure.
"""

# Standard library
from glob import glob
import json
import logging
import os
from pathlib import Path

# Local imports
from source.collection.video import Video
from source.constants import *
from source.filter import Filter
from source.utils.helper import default_serializer, file_write

# Third-party packages
# N/A

# TODO: Moving files needs to take associated subtitles, at the very least.
#       consider adding a function that searches for the files with an
#       identical prefix but different extension. key:value pair could be
#       filename:type, ie video.srt:subtitles


class Collection:
    def __init__(self, path=None):
        self.videos = {}
        if path is not None:
            self.path = path
        else:
            self.path = Path(os.getenv('SOURCE_PATH'))

    def add_video(self, path: Path):
        video = Video.from_file(path)
        self.videos.update({video.get_hash(): video})
        logging.info(f"Added '{path}' to collection")

    @staticmethod
    def apply_filter(videos, filter_string):
        f = Filter.from_string(filter_string)
        return [video
                for video
                in videos
                if f.matches(video.get_pref_data(f.key))]

    @staticmethod
    def from_dict(d):
        # Todo: Validate input dictionary
        new = Collection()
        for sha_256, nested_dictionary in d:
            new.videos.update({sha_256, Video.from_dict(nested_dictionary)})

    @staticmethod
    def from_json(j):
        return Collection.from_dict(json.loads(j))

    def get_video(self, sha_256):
        return self.videos.get(sha_256)

    def get_videos(self, filter_strings=None):
        ret = self.videos.values()
        if filter_strings:
            for string in filter_strings:
                ret = self.apply_filter(ret, string)
        return ret

    def metadata_load(self, path: Path = None) -> None:
        if path is None:
            path = Path('./metadata.json')

        with path.open('r') as file:
            serializable = json.load(file)

        for sha_256, data in serializable.items():
            video = Video()
            video.data = data
            self.videos.update({sha_256: video})

    def metadata_save(self, path="./metadata.json"):
        file_write(path, self.to_json())

    def organize_files(self, dest):
        pass

    def scan_directory(self, path: Path) -> None:
        if not path.is_dir():
            raise NotADirectoryError(f"Path '{path}' must point to a directory. To scan a file, use scan_file()")
        else:
            for glob_path in path.rglob('*'):
                if glob_path.is_file():
                    self.scan_file(glob_path)

    def scan_file(self, path: Path) -> None:
        if not path.is_file():
            raise IsADirectoryError(f"Path '{path}' must point to a file. To scan a directory, use scan_directory()")
        elif path.suffix[1:] in VIDEO_EXTENSIONS:
            self.add_video(path)

    def scan_path(self, path: Path) -> None:
        if not path.exists():
            raise ValueError(f"'{path}' is not recognized by the OS as a valid path")
        if path.is_dir():
            self.scan_directory(path)
        elif path.is_file():
            self.scan_file(path)

    def scan_path_list(self, path_list: list) -> None:
        for path in path_list:
            self.scan_path(path)

    def scan_glob(self, path: Path, wildcard_expression: str, recurse=False) -> None:
        if recurse:
            paths = path.rglob(wildcard_expression)
        else:
            paths = path.glob(wildcard_expression)
        self.scan_path_list(list(paths))

    def to_dict(self, filter_strings=None):
        filtered = self.get_videos(filter_strings)
        return {
            video.get_hash(): video.data
            for video
            in filtered
        }

    def to_json(self, filter_strings=None):
        return json.dumps(self.to_dict(filter_strings),
                          indent=4,
                          skipkeys=True,
                          default=default_serializer)

    def update_api_data(self, api, **kwargs):
        """
        Updates all videos with data fetched from supplied API plugin
        :param api: API plugin to fetch data
        :param kwargs: Keyword arguments to pass to API plugin
        :return: None
        """

        for video in self.videos.values():
            video.update_api_data(api, **kwargs)
