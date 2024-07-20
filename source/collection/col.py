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
from source.api.api_manager import APIManager
from source.collection.video import Video
from source.command.combuffer import CommandBuffer
from source.constants import *
from source.utils.helper import default_serializer
from source.utils.helper import file_write


# TODO: Moving files needs to take associated subtitles, at the very least.
#       consider adding a function that searches for the files with an
#       identical prefix but different extension. key:value pair could be
#       filename:type, ie video.srt:subtitles


class Collection:
    def __init__(self, path=None):
        self.videos = {}
        self.cb = CommandBuffer()
        if path:
            self.metadata_load(path)

    def add_video(self, path):
        video = Video()
        video.update_file_data(path)
        self.videos.update({video.get_hash(): video})
        # TODO: logging output conflicts with tqdm, output is messy
        logging.info(f"Added '{path}' to collection")

    def get_video(self, hash):
        return self.videos.get(hash)

    def metadata_load(self, path="./metadata.json"):
        with open(path, 'r') as file:
            serializable = json.load(file)

        for entry in serializable:
            video = Video()
            video.data = serializable.get(entry)
            self.videos.update({entry: video})

    def metadata_save(self, path="./metadata.json"):
        file_write(path, self.to_json())

    def organize_files(self, dest):
        # TODO: This ought to create (and return?) a transaction (command buffer)
        #       Then we give the user a chance to preview it
        #       Finally the user may execute the transaction

        cb = CommandBuffer()
        os.makedirs(dest, exist_ok=True)
        for video in self.videos.values():
            vid_dest = os.path.join(dest, video.generate_dir_name())
            cb.add_move_video(video, vid_dest)
        cb.preview_buffer()
        cb.validate_exec_buffer()
        # get user confirmation
        # cb.execute_cmd_buffer()

    def scan_directory(self, path):
        # TODO: standardize use of path, filename, and root or dir
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(VIDEO_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    self.add_video(file_path)

    def to_json(self):
        return json.dumps({hash: video.data for hash, video in self.videos.items()},
                          indent=4,
                          skipkeys=True,
                          default=default_serializer)

    def update_api_data(self):
        api_man = APIManager()
        api_man.discover_apis()
        apis = api_man.get_api_names()
        for vid in self.videos:
            for api in apis:
                if api.get_name() not in vid.get_source_names():
                    vid.update_api_data(api)

    def update_guessit(self):
        for video in self.videos.values():
            video.update_guessit()

    def update_omdb(self):
        for video in self.videos:
            video.update_omdb()
