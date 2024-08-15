# ./source/session/session_man.py

"""
    Manages the current session, including the state of the collection
    and the command buffer
"""

# Standard library
from pathlib import Path
from typing import Optional

# Local imports
from source.api.api_manager import APIManager
from source.collection.col import Collection
from source.command.combuffer import CommandBuffer
from source.command.update_video_data import UpdateVideoData
from source.command.move_video import MoveVideo

from source.utils.helper import file_write, get_files_from_path, parse_glob_string, generate_destination_paths

# Third-party packages
# n\a


class PyvorgSession:
    # Todo: Decouple components once we get things hammered out
    def __init__(self):
        self.api_manager = APIManager()
        self.command_buffer = CommandBuffer()
        self.collection = Collection()
        # TODO: Decide whether this should be done by APIManager's constructor
        self.api_manager.init_plugins()

    def clear_staged_operations(self) -> None:
        self.command_buffer.clear_exec_buffer()

    def commit_staged_operations(self) -> None:
        self.command_buffer.execute_cmd_buffer()

    def export_collection_metadata(self, path: Path, filter_strings=None) -> None:
        file_write(path, self.collection.to_json(filter_strings))

    def get_transaction_preview(self) -> str:
        return str(self.command_buffer)

    def scan_files_in_path(self, path_string: str, recursive: bool = False) -> None:
        root, glob_pattern = parse_glob_string(path_string)
        files = get_files_from_path(root, recursive, glob_pattern)
        self.collection.add_files(files)

    def stage_organize_video_files(self, filter_strings: Optional[list[str]] = None) -> None:
        videos = self.collection.get_videos(filter_strings)
        paths = generate_destination_paths(videos)
        params = zip(videos, paths)
        # TODO: We should abstract this further so we can stage commands in one call to a CommandBuffer method
        cmds = self.command_buffer.build_commands(MoveVideo, params)
        self.command_buffer.stage_commands(cmds)

    def stage_update_api_metadata(self, api_names: list[str], filter_strings: Optional[list[str]]) -> None:
        videos = self.collection.get_videos(filter_strings)
        apis = self.api_manager.get_apis(api_names)
        params = zip(videos, apis)
        cmds = self.command_buffer.build_commands(UpdateVideoData, params)
        self.command_buffer.stage_commands(cmds)

    def undo_transaction(self) -> None:
        self.command_buffer.execute_undo_buffer()
