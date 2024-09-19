# source.collection.py

"""
    Collection class handles storing videos, and retrieving subsets
    of the collection by applying filters
"""

# Standard library
import logging
from pathlib import Path
from typing import Optional

# Local imports
from source.state.video import Video
from source.service.file_svc import get_file_type
from source.service.video_svc import create_video_from_file_path

# Third-party packages
# N/A


# TODO: Implement support for other media
#       Add methods:
#           add_poster_file()
#           add_trailer_file()
#           add_subtitle_file()

class Collection:
    def __init__(self):
        self.videos = {}

    def add_file(self, file_path: Path) -> Optional[Video]:
        # TODO: Consider factoring this out so that Collection
        #       doesn't need to use FileService
        new = None
        if get_file_type(file_path) == 'video':
            new = self.add_video_file(file_path)
        return new
        # Placeholder for other media types

    def add_files(self, file_paths: list[Path]) -> list[Video]:
        added = []
        for path in file_paths:
            new = self.add_file(path)
            if new:
                added.append(new)
        return added

    def add_video_file(self, file_path: Path) -> Video:
        new_video = create_video_from_file_path(file_path)
        self.videos.update({new_video.get_hash(): new_video})
        logging.info(f"Added '{file_path}' to collection")
        return new_video

    def add_video_instance(self, video: Video) -> Optional[str]:
        video_id = self.generate_video_id(video)
        self.videos.update({video_id: video})
        return video_id

    @staticmethod
    def generate_video_id(video: Video):
        return video.get_hash()

    def get_video_ids(self):
        return self.videos.keys()

    def get_video(self, key: str) -> Video:
        return self.videos.get(key)

    def get_videos(self) -> list[Video]:
        return list(self.videos.values())

    def remove_from_collection(self, videos: list[Video]) -> None:
        self.videos = {
            key: value
            for key, value
            in self.videos.items()
            if value not in videos
        }

    def to_dict(self) -> dict:
        return {
            video.get_hash(): video.data
            for video
            in self.get_videos()
        }
    #
    # def to_json(self) -> str:
    #     return json.dumps(self.to_dict(),
    #                       indent=4,
    #                       skipkeys=True,
    #                       default=default_serializer)
