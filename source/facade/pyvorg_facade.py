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
from source.service import cmd_svc as cmd_svc, \
                           config_svc as cfg_svc, \
                           collection_svc as col_svc, \
                           file_svc as file_svc, \
                           plugin_svc as plugin_svc, \
                           serialize_svc as serial_svc, \
                           video_svc as video_svc

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
        cmd_svc.clear_exec_buffer(self.command_buffer)

    def commit_staged_operations(self) -> None:
        cmd_svc.execute_cmd_buffer(self.command_buffer)

    def export_collection_metadata(self, path: Path) -> None:
        metadata = col_svc.get_metadata(self.collection)
        write_data = serial_svc.dict_to_json(metadata)
        file_svc.file_write(path, write_data)

    def get_preview_of_staged_operations(self) -> str:
        return cmd_svc.get_exec_preview(self.command_buffer)

    def import_collection_metadata(self, path: Path) -> None:
        metadata = file_svc.file_read(path)
        col_svc.validate_metadata(metadata)
        col_svc.import_metadata(self.collection, metadata)

    def scan_files_in_path(self,
                           path_string: str,
                           recursive: bool = False) -> None:
        root, glob_pattern = file_svc.parse_glob_string(path_string)
        file_paths = file_svc.get_files_from_path(root, recursive, glob_pattern)
        videos = video_svc.create_videos_from_file_paths(file_paths)
        col_svc.add_videos(self.collection, videos)

    def save_state(self):
        collection_path = cfg_svc.get_default_collection_path()
        command_buffer_path = cfg_svc.get_default_command_buffer_path()
        serialized_collection = serial_svc.obj_to_pickle(self.collection)
        serialized_command_buffer = serial_svc.obj_to_pickle(self.command_buffer)
        file_svc.file_write_bytes(collection_path, serialized_collection)
        file_svc.file_write_bytes(command_buffer_path, serialized_command_buffer)

    def load_state(self):
        collection_path = cfg_svc.get_default_collection_path()
        command_buffer_path = cfg_svc.get_default_command_buffer_path()
        serialized_collection = file_svc.file_read_bytes(collection_path)
        serialized_command_buffer = file_svc.file_read_bytes(command_buffer_path)
        self.collection = serial_svc.pickle_to_object(serialized_collection)
        self.command_buffer = serial_svc.pickle_to_object(serialized_command_buffer)

    def stage_organize_video_files(self,
                                   destination: Optional[str] = None,
                                   format_str: Optional[str] = None,
                                   filter_strings: Optional[list[str]] = None) -> None:
        if destination is None:
            destination = cfg_svc.get_default_organize_path()
        if format_str is None:
            format_str = cfg_svc.get_default_format_str()

        videos = col_svc.get_filtered_videos(self.collection, filter_strings)
        paths = video_svc.generate_destination_paths(videos, destination, format_str)
        cmd_arg_tuples = zip(videos, paths)
        cmd_kwarg_dicts = repeat({})
        cmds = cmd_svc.build_commands('MoveVideo', cmd_arg_tuples, cmd_kwarg_dicts)
        cmd_svc.stage_commands(self.command_buffer, cmds)

    def stage_update_api_metadata(self,
                                  api_name: str,
                                  filter_strings: Optional[list[str]] = None) -> None:

        videos = col_svc.get_filtered_videos(self.collection, filter_strings)
        api_instance = plugin_svc.get_plugin_instance(api_name, source.datafetchers)
        req_plugin_params = plugin_svc.get_required_params(api_instance)
        cmd_args_tuples = zip(videos, repeat(api_instance))
        cmd_kwargs_dicts = video_svc.build_cmd_kwargs(videos, req_plugin_params)
        cmds = cmd_svc.build_commands('UpdateVideoData', cmd_args_tuples, cmd_kwargs_dicts)
        cmd_svc.stage_commands(self.command_buffer, cmds)

    def undo_transaction(self) -> None:
        cmd_svc.execute_undo_buffer(self.command_buffer)
