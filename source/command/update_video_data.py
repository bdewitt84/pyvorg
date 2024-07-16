# source/command/update_video_data.py

"""
    Implementation of UpdateVideoData command used by CommandBuffer
"""

# Standard library

# Local imports
from source.command.command import Command

# Third-party packages


class UpdateVideoData(Command):
    def __init__(self, video, api, **kwargs):
        self.undo_data = None
        self.video = video
        self.api = api
        self.kwargs = kwargs

    def exec(self):
        api_name = self.api.get_name()
        self.undo_data = self.video.get_api_data(api_name)
        data = self.api.fetch_video_data(self.kwargs)
        self.video.set_api_data(api_name, data)

    def undo(self):
        if self.undo_data is None:
            self.video.data.pop(self.api.get_name())
        else:
            self.video.set_api_data(self.api.get_name(), self.undo_data)
        self.undo_data = None

    def validate_exec(self):
        # command will fail if the video does not exist
        # if the api is not valid
        # if the api is not accessible
        pass

    def validate_undo(self):
        pass