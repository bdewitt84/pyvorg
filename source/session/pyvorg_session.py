# ./source/session/pyvorg_session.py

"""
    Acts as entry point for user interface.
    Should only interact with the service layer.
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

from source.utils import cmdservice as cmdsvc,\
                         collectionservice as colsvc,\
                         fileservice as filesvc,\
                         pluginservice as pluginsvc,\
                         stateservice as statesvc,\
                         videoservice as vidsvc

# Third-party packages
# n\a


# TODO: Moving file_paths needs to take associated subtitles, at the very least.
#       consider adding a function that searches for the file_paths with an
#       identical prefix but different extension. key:value pair could be
#       filename:type, ie video.srt:subtitles


class PyvorgSession:
    # Todo: Decouple components once we get things hammered out
    def __init__(self):
        self.command_buffer = CommandBuffer()
        self.collection = Collection()

    def clear_staged_operations(self) -> None:
        cmdsvc.clear_exec_buffer(self.command_buffer)

    def commit_staged_operations(self) -> None:
        cmdsvc.execute_cmd_buffer(self.command_buffer)

    def export_collection_metadata(self, path: Path, filter_strings=None) -> None:
        # metadata = self.collection.to_json(filter_strings)
        metadata = colsvc.get_metadata(self.collection)
        filesvc.file_write(path, metadata)

    def get_preview_of_staged_operations(self) -> str:
        # return str(self.command_buffer)
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

    def stage_organize_video_files(self, filter_strings: Optional[list[str]] = None) -> None:
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        paths = vidsvc.generate_destination_paths(videos)
        params = zip(videos, paths)
        cmds = cmdsvc.build_commands('MoveVideo', params)
        cmdsvc.stage_commands(cmds)

    def stage_update_api_metadata(self, api_name: str, filter_strings: Optional[list[str]]) -> None:
        videos = colsvc.get_filtered_videos(self.collection, filter_strings)
        api = pluginsvc.get_apis(api_name)
        req_params = pluginsvc.get_reqired_params(api)
        filler = vidsvc.get_metadata(videos, req_params)
        filled_params = pluginsvc.fill_params(req_params, filler)
        cmdsvc.build_commands('UpdateVideoData', videos, filled_params)

    def undo_transaction(self) -> None:
        # self.command_buffer.execute_undo_buffer()
        cmdsvc.execute_buffer(self.command_buffer)