# source/command/update_video_data.py

"""
    Implementation of UpdateVideoData command used by CommandBuffer
"""

# Standard library
import json

# Local imports
from source.command.command import Command
from source.utils.helper import update_api_data

# Third-party packages
# n/a


class UpdateVideoData(Command):
    def __init__(self, video, api, **kwargs):
        self.undo_data = None
        self.video = video
        self.api = api
        self.kwargs = kwargs

    def exec(self):
        self.undo_data = self.video.get_source_data(self.api.get_name)
        update_api_data(self.video, self.api)

    def undo(self):
        if self.undo_data is None:
            self.video.data.pop(self.api.get_name())
        else:
            self.video.set_source_data(self.api.get_name(), self.undo_data)
        self.undo_data = None

    def validate_exec(self):
        # command will fail if the video does not exist
        # if the api is not valid
        # if the api is not accessible
        pass

    def validate_undo(self):
        pass

    def __str__(self):
        return f"Fetch '{self.api.get_name()}' data for '{self.video.get_path()}'"
