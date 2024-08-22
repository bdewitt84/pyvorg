# source/utils/videoservice/py

# Standard library
from pathlib import Path
import re

# Local imports
from source.collection.video import Video

# Third-party packages


def create_videos_from_file_paths(file_paths: list[Path]):
    return [Video.from_file(path) for path in file_paths]


def generate_destination_paths(videos, dst_tree: Path = None):
    return [dst_tree / generate_str_from_metadata(video) for video in videos]


def generate_str_from_metadata(self, format_string: str = '%title (%year)') -> str:
    matches = re.findall(r"(%\w+)(=[\w()_,.]*)?", format_string)
    for specifier, default_value in matches:
        metadata_value = self.get_pref_data(specifier[1:], default_value[1:])
        format_string = format_string.replace(specifier+default_value, metadata_value)
    return format_string
