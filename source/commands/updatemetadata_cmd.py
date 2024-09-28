# source/command/updatemetadata_cmd.py

"""
    Implementation of UpdateVideoData command used by CommandBuffer
"""

# Standard library

# Local imports
from source.commands.command_base import Command
from source.datasources.base_metadata_source import MetadataSource
from source.state.mediafile import MediaFile

# Third-party packages
# n/a


class UpdateVideoData(Command):
    def __init__(self, video: MediaFile, api: MetadataSource, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_data = None
        self.video = video
        self.api = api
        self.kwargs = kwargs
        self.metadata = None

    def exec(self):
        self._update_undo_data()
        self._get_video_metadata()
        self._update_video_metadata()

    def _update_undo_data(self):
        self.undo_data = self.video.get_source_data(self.api.get_name())

    def _get_video_metadata(self):
        self.metadata = self.api.fetch_data(**self.kwargs)

    def _update_video_metadata(self):
        self.video.set_source_data(self.api.get_name(), self.metadata)

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
