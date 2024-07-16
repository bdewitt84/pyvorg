# source/command/update_video_data.py

"""
    Implementation of UpdateVideoData command used by CommandBuffer
"""

# Standard library
import os
import logging

# Local imports
from source.command.command import Command

# Third-party packages


# TODO: Implement this
class UpdateVideoData(Command):
    def __init__(self, video, api, **kwargs):
        self.undo_data = None
        self.video = video
        self.api = api
        self.kwargs = kwargs

    def exec(self):
        if self.api.get_name() in self.video.data.keys():
            self.undo_data = self.video.data[self.api.get_name()]
        self.api.fetch_video_data(self.kwargs)

    def undo(self):
        if self.undo_data is not None:
            self.video.set_api_data()

    def validate_exec(self):
        pass

    def validate_undo(self):
        pass
