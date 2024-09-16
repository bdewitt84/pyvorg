# source/service/videoservice/py

# Standard library
from pathlib import Path
import re

# Local imports
from source.state.video import Video

# Third-party packages


# TODO: Refactor to media_service.py
#       add methods:
#           create_posters_from_file_paths()
#           create_trailers_from_file_paths()


def build_cmd_kwargs(videos: list[Video], req_params: list[str]) -> list[dict]:
    list_of_param_dicts: [dict] = []
    for video in videos:
        cur_dict = {}
        for param in req_params:
            cur_dict.update(
                {param: video.get_pref_data(param)}
            )
        list_of_param_dicts.append(cur_dict)
    return list_of_param_dicts


def create_videos_from_file_paths(file_paths: list[Path]) -> list[Video]:
    return [Video.from_file(path) for path in file_paths]


def generate_destination_paths(videos, dst_tree: Path, format_string: str) -> list[Path]:
    return [Path(dst_tree) / generate_str_from_metadata(video, format_string) for video in videos]


def generate_destination_path(video, dst_tree: Path, format_string: str) -> Path:
    return Path(dst_tree) / generate_str_from_metadata(video, format_string)


def generate_str_from_metadata(video, format_string: str) -> str:
    matches = re.findall(r"(%\w+)(=[\w()_,.]*)?", format_string)
    for specifier, default_value in matches:
        metadata_value = video.get_pref_data(specifier[1:], default_value[1:])
        format_string = format_string.replace(specifier+default_value, metadata_value)
    return format_string.strip()


def update_file_data(video: Video, path: Path, skip_hash: bool) -> None:
    video.update_file_data(path, skip_hash)
