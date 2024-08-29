# ./source/facade/pyvorg_facade.py

"""
    Acts as entry point for user interface.
    Should only interact with the service layer.
"""

# Standard library
from itertools import repeat
from pathlib import Path
from typing import Optional

# Local imports
from source.state.col import Collection
from source.state.combuffer import CommandBuffer
import source.datafetchers
from source.service import cmd_svc as cmdsvc, \
                           config_svc as cfg_svc, \
                           collection_svc as colsvc, \
                           file_svc as filesvc, \
                           plugin_svc as pluginsvc, \
                           serialize_svc as serial_svc, \
                           video_svc as vidsvc

# Third-party packages
# n\a


# TODO: Moving file_paths needs to take associated subtitles, at the very least.
#       consider adding a function that searches for the file_paths with an
#       identical prefix but different extension. key:value pair could be
#       filename:type, ie video.srt:subtitles


class Facade:
    # Todo: Decouple components once we get things hammered out
    def __init__(self, collection: Collection, command_buffer: CommandBuffer):
        self.collection = collection
        self.command_buffer = command_buffer

    def clear_staged_operations(self) -> None:
        cmdsvc.clear_exec_buffer(self.command_buffer)

    def commit_staged_operations(self) -> None:
        cmdsvc.execute_cmd_buffer(self.command_buffer)

    def export_collection_metadata(self, path: Path) -> None:
        metadata = colsvc.get_metadata(self.collection)
        write_data = serial_svc.dict_to_json(metadata)
        filesvc.file_write(path, write_data)

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

    def stage_organize_video_files(self,
                                   destination: Optional[str] = None,
                                   format_str: Optional[str] = None,
                                   filter_strings: Optional[list[str]] = None) -> None:
        # Assign defaults
        if destination is None:
            destination = cfg_svc.get_default_organize_path()
        if format_str is None:
            format_str = cfg_svc.get_default_format_str()
        # Collect argument data
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        paths = vidsvc.generate_destination_paths(videos, destination, format_str)
        print(paths)
        # Pack arguments
        cmd_arg_tuples = zip(videos, paths)
        # Pack (empty) kwargs
        cmd_kwarg_dicts = [{} for _ in range(len(videos))]
        # Build commands
        cmds = cmdsvc.build_commands('MoveVideo', cmd_arg_tuples, cmd_kwarg_dicts)
        print(cmds)
        # Stage commands
        cmdsvc.stage_commands(self.command_buffer, cmds)

    def stage_update_api_metadata(self, api_name: str, filter_strings: Optional[list[str]]) -> None:
        # Collect parameter data
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        api_instance = pluginsvc.get_plugin_instance(api_name, source.datafetchers)
        req_plugin_params = pluginsvc.get_required_params(api_instance)
        cmd_kwargs_dicts = vidsvc.build_cmd_kwargs(videos, req_plugin_params)
        # Pack args
        cmd_args_tuples = zip(videos, repeat(api_instance))
        # Build commands
        cmds = cmdsvc.build_commands('UpdateVideoData', cmd_args_tuples, cmd_kwargs_dicts)
        # Stage commands
        cmdsvc.stage_commands(self.command_buffer, cmds)

    def undo_transaction(self) -> None:
        cmdsvc.execute_undo_buffer(self.command_buffer)
