# ./source/session/session_man.py

"""
    Manages the current session, including the state of the collection
    and the command buffer
"""

# Standard library
import os
import pickle

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
        self.col = Collection()
        self.cb = CommandBuffer()
        self.apiman = APIManager()
        self.apiman.init_plugins()

    # def load_session(self, path):
    #     data = file_read(path)
    #     unserialized = json.loads(data)
    #     # validate unserialized state
    #     col_dict = unserialized.get('col')
    #     cb_dict = unserialized.get('cb')
    #
    #     self.col = Collection.from_dict()
    #     self.cb = CommandBuffer.from_dict()
    #
    #     # TODO: we need to reconnect API instances as a part of de-serialization.
    #     #       to do this, we should traverse parts of the dict where APIs would
    #     #       have been before serialization.
    #
    # def save_session(self, path='./session.j son'):
    #     # check if it exists, ask to overwrite
    #     state = {
    #         'col': self.col.to_dict(),
    #         'cb': self.cb.to_dict()
    #     }
    #     serialized = json.dumps(state)
    #     file_write(path, serialized)

    def commit_transaction(self):
        self.cb.execute_cmd_buffer()

    def export_collection_metadata(self, path):
        data = self.col.to_json()
        file_write(path, data)

    def pickle_session(self, path='./session.pickle'):
        with open(path, 'wb') as file:
            pickle.dump(self, file)

    def preview_transaction(self):
        return self.cb.__str__()

    def set_profile(self):
        pass

    def scan_path(self, path):
        if os.path.isdir(path):
            self.col.scan_directory(path)
        elif os.path.isfile(path):
            self.col.scan_file(path)
        else:
            raise ValueError(f"'{path}' is not recognized by the OS as a valid path")

    def stage_organize_video_files(self):
        for video in self.col.get_videos():
            dest = os.path.join(os.getenv('DEST_PATH'), video.generate_dir_name())
            cmd = MoveVideo(video, dest)
            self.cb.add_command(cmd)

    def stage_update_api_metadata(self, api):
        for video in self.col.get_videos():
            cmd = UpdateVideoData(video, api)
            self.cb.add_command(cmd)

    def undo_transaction(self):
        self.cb.execute_undo_buffer()

    @staticmethod
    def unpickle_session(path='./session.pickle'):
        with open(path, 'rb') as file:
            return pickle.load(file)
