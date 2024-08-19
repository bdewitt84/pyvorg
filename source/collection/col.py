# source.collection.py

"""
    Collection class handles storing videos, and retrieving subsets
    of the collection by applying filters
"""

# Standard library
import json
import logging
import os
from pathlib import Path

# Local imports
from source.collection.video import Video
from source.utils.helper import default_serializer
from source.utils.fileservice import get_file_type

# Third-party packages
# N/A


class Collection:
    def __init__(self, path: Path = None):
        self.videos = {}
        if path is not None:
            self.path = path
        else:
            # TODO: Make/Use getter in helper module for this
            self.path = Path(os.getenv('SOURCE_PATH'))

    def add_file(self, file_path: Path) -> None:
        # TODO: Refactor to service later
        if get_file_type(file_path) == 'video':
            self.add_video_file(file_path)
        # Placeholder for other media types

    def add_files(self, file_paths: list[Path]) -> None:
        # TODO: Refactor to service later
        for path in file_paths:
            self.add_file(path)

    def add_video_file(self, file_path: Path) -> None:
        # TODO: Refactor to service later
        new_video = Video.from_file(file_path)
        self.videos.update({new_video.get_hash(): new_video})
        logging.info(f"Added '{file_path}' to collection")

    def add_video_instance(self, video: Video) -> None:
        self.videos.update({self.generate_video_id(video): video})

    @staticmethod
    def apply_filter(videos, filter_string) -> list[Video]:
        f = Filter.from_string(filter_string)
        return [video for video in videos if f.matches(video.get_pref_data(f.key))]

    @staticmethod
    def from_dict(source: dict):
        # Todo: Validate input dictionary
        new_col = Collection()
        for nested_dictionary in source.values():
            new_vid = Video.from_dict(nested_dictionary)
            new_col.add_video_instance(new_vid)
        return new_col

    @staticmethod
    def from_json(source: str):
        return Collection.from_dict(json.loads(source))

    @staticmethod
    def generate_video_id(video: Video):
        return video.get_hash()

    def get_video(self, key: str) -> Video:
        return self.videos.get(key)

    def get_videos(self, filter_strings=None) -> list[Video]:
        ret = self.videos.values()
        if filter_strings:
            for string in filter_strings:
                ret = self.apply_filter(ret, string)
        return ret

    def remove_from_collection(self, videos: list[Video]) -> None:
        self.videos = {
            key: value
            for key, value
            in self.videos.items()
            if value not in videos
        }

    def to_dict(self, filter_strings: str = None) -> dict:
        filtered = self.get_videos(filter_strings)
        return {
            video.get_hash(): video.data
            for video
            in filtered
        }

    def to_graph(self):
        # TODO: Implement later
        pass

    def to_json(self, filter_strings: str = None) -> str:
        return json.dumps(self.to_dict(filter_strings),
                          indent=4,
                          skipkeys=True,
                          default=default_serializer)

    def to_tsv(self):
        # TODO: Implement later
        pass
