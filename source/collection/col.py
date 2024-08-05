# source.col.py

"""
    Collection class handles the main functionality of the package, including
    scanning for files, updating the metadata from online sources, and organizing
    the video files into a predefined file structure.
"""

# Standard library
import json
import logging
import os

# Local imports
from source.collection.video import Video
from source.constants import *
from source.filter import Filter
from source.utils.helper import default_serializer
from source.utils.helper import file_write

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
            self.path = os.getenv('SOURCE_PATH')

    def add_video(self, path):
        video = Video()
        video.update_file_data(path)
        self.videos.update({video.get_hash(): video})
        logging.info(f"Added '{path}' to collection")

    @staticmethod
    def filter_videos(videos, string):
        f = Filter.from_string(string)
        return [video
                for video
                in videos
                if f.matches(video.get_pref_data(f.key))]

    @staticmethod
    def from_dict(d):
        # Todo: Validate input dictionary
        new = Collection()
        for hash, dict in d:
            new.videos.update({hash, Video.from_dict(dict)})

    @staticmethod
    def from_json(j):
        return Collection.from_dict(json.loads(j))

    def get_video(self, hash):
        return self.videos.get(hash)

    def get_videos(self, filter_string=None):
        ret = self.videos.values()
        if filter is not None:
            ret = self.filter_videos(ret, filter_string)
        return ret

    def metadata_load(self, path="./metadata.json"):
        with open(path, 'r') as file:
            serializable = json.load(file)

        for entry in serializable:
            video = Video()
            video.data = serializable.get(entry)
            self.videos.update({entry: video})

    def metadata_save(self, path="./metadata.json"):
        file_write(path, self.to_json())

    # def organize_files(self, dest):
    #
    #     cb = CommandBuffer()
    #     os.makedirs(dest, exist_ok=True)
    #     for video in self.videos.values():
    #         vid_dest = os.path.join(dest, video.generate_dir_name())
    #         cb.add_move_video(video, vid_dest)
    #     cb.preview_buffer()
    #     cb.validate_exec_buffer()
    #     # get user confirmation
    #     # cb.execute_cmd_buffer()

    def scan_directory(self, path):
        # TODO: standardize use of path, filename, and root or dir. Currently, slashes go both ways.
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.scan_file(file_path)
        else:
            raise NotADirectoryError(f"Path '{path}' must point to a directory. To scan a file, use scan_file()")

    def scan_file(self, path):
        if os.path.isfile(path):
            if path.endswith(VIDEO_EXTENSIONS):
                self.add_video(path)
        else:
            raise IsADirectoryError(f"Path '{path}' must point to a file. To scan a directory, use scan_directory()")

    def scan_path(self, path):
        if os.path.isdir(path):
            self.scan_directory(path)
        elif os.path.isfile(path):
            self.scan_file(path)
        else:
            raise ValueError(f"'{path}' is not recognized by the OS as a valid path")

    def to_dict(self):
        return {
            hash: video.data
            for hash, video
            in self.videos.items()
        }

    def to_json(self):
        return json.dumps(self.to_dict(),
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
