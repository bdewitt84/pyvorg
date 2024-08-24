# ./source/facade/facade.py

"""
    Acts as entry point for user interface.
    Should only interact with the service layer.
"""

# Standard library
from itertools import repeat
from pathlib import Path
from typing import Optional


# Local imports
from state.col import Collection
from state.combuffer import CommandBuffer

from service import cmdservice as cmdsvc,\
                    configservice as cfg_svc,\
                    videoservice as vidsvc,\
                    collectionservice as colsvc,\
                    pluginservice as pluginsvc,\
                    fileservice as filesvc


# Third-party packages
# n\a


# TODO: Moving file_paths needs to take associated subtitles, at the very least.
#       consider adding a function that searches for the file_paths with an
#       identical prefix but different extension. key:value pair could be
#       filename:type, ie video.srt:subtitles


class Facade:
    # Todo: Decouple components once we get things hammered out
    def __init__(self):
        self.command_buffer = CommandBuffer()
        self.collection = Collection()

    def clear_staged_operations(self) -> None:
        cmdsvc.clear_exec_buffer(self.command_buffer)

    def commit_staged_operations(self) -> None:
        cmdsvc.execute_cmd_buffer(self.command_buffer)

    def export_collection_metadata(self, path: Path, filter_strings=None) -> None:
        metadata = colsvc.get_metadata(self.collection, filter_strings)
        filesvc.file_write(path, metadata)

    def get_preview_of_staged_operations(self) -> str:
        return cmdsvc.get_exec_preview(self.command_buffer)

    def import_collection_metadata(self, path: Path) -> None:
        metadata = filesvc.file_read(path)
        colsvc.validate_metadata(metadata)
        colsvc.import_metadata(self.collection, metadata)

    def scan_files_in_path(self, path_string: str, recursive: bool = False) -> None:
        root, glob_pattern = filesvc.parse_glob_string(path_string)
        file_paths = filesvc.get_files_from_path(root, recursive, glob_pattern)
        videos = vidsvc.create_videos_from_file_paths(file_paths)
        colsvc.add_videos(self.collection, videos)

    def stage_organize_video_files(self, format_str: Optional[str] = None, filter_strings: Optional[list[str]] = None) -> None:
        # Assign defaults
        if format_str is None:
            format_str = cfg_svc.get_default_format_str()
        # Collect parameter data
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        paths = vidsvc.generate_destination_paths(videos, format_str)
        # Pack parameters
        params = zip(videos, paths)
        # Build commands
        cmds = cmdsvc.build_commands('MoveVideo', params)
        # Stage commands
        cmdsvc.stage_commands(self.command_buffer, cmds)

    def stage_update_api_metadata(self, api_name: str, filter_strings: Optional[list[str]]) -> None:
        # Collect parameter data
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        api_instance = pluginsvc.get_plugin_instance(api_name)
        req_plugin_params = pluginsvc.get_required_params(api_instance)
        cmd_kwargs = vidsvc.build_cmd_kwargs(videos, req_plugin_params)
        # Pack parameters
        params = zip(videos, repeat(api_instance), cmd_kwargs)
        # Build commands
        cmds = cmdsvc.build_commands('UpdateVideoData', params)
        # Stage commands
        cmdsvc.stage_commands(self.command_buffer, cmds)

    def undo_transaction(self) -> None:
        cmdsvc.execute_undo_buffer(self.command_buffer)
