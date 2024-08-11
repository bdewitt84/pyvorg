# ./source/session/session_man.py

"""
    Manages the current session, including the state of the collection
    and the command buffer
"""

# Standard library
import os
from pathlib import Path

# Local imports
from source.api.api_manager import APIManager
from source.collection.col import Collection
from source.command.combuffer import CommandBuffer
from source.command.update_video_data import UpdateVideoData
from source.command.move_video import MoveVideo

from source.utils.helper import file_write

# Third-party packages
# n\a


class SessionManager:
    def __init__(self, path='./session.json'):
        self.apiman = APIManager()
        self.cb = CommandBuffer()
        self.col = Collection()
        self.profile_path = path

        self.apiman.init_plugins()

    def clear_transaction(self):
        self.cb.clear_exec_buffer()

    def commit_transaction(self):
        self.cb.execute_cmd_buffer()

    def export_collection_metadata(self, path, filter_strings=None):
        file_write(path, self.col.to_json(filter_strings))

    def get_transaction_preview(self):
        return self.cb.__str__()

    def scan_glob(self, glob_string: Path):
        root = glob_string.parent
        glob = glob_string.name
        self.col.scan_glob(root, glob)

    def scan_path(self, path_string):
        if '*' in path_string:
            self.scan_glob(Path(path_string))
        else:
            path_obj = Path(path_string).resolve()
            self.col.scan_path(path_obj)

    def stage_organize_video_files(self, filter_strings=None):
        videos = self.col.get_videos(filter_strings)
        for video in videos:
            dest = Path(os.getenv('DEST_PATH')) / video.generate_dir_name()
            cmd = MoveVideo(video, dest)
            self.cb.add_command(cmd)

    def stage_update_api_metadata(self, api_name, filter_strings=None):
        api = self.apiman.get_api(api_name)
        videos = self.col.get_videos(filter_strings)
        for video in videos:
            cmd = UpdateVideoData(video, api)
            self.cb.add_command(cmd)

    def undo_transaction(self):
        self.cb.execute_undo_buffer()
