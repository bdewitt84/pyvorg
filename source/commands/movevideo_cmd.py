# source/command/movevideo_cmd.py

"""
Implementation of MoveVideoCmd command used by CommandBuffer
"""

# Standard library
from pathlib import Path

# Local imports
from source.commands.command_base import Command
from source.state.mediafile import MediaFile
from source.utils import fileutils
from source.utils.videoutils import generate_destination_path

# Third-party packages


# TODO: Refactor to move_media_file.py


class MoveVideoCmd(Command):
    def __init__(self,
                 video: MediaFile,
                 target_root: Path,
                 format_string: str,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.video = video
        self.target_root = target_root.resolve()
        self.target_subdir = None
        self.target_file_path = None
        self.format_string = format_string
        self.origin_dir = None
        self.created_dirs = []

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.target_root}\n"

    def exec(self) -> None:
        self._update_origin_dir()
        self._update_target_file_path()
        self._make_dirs()
        self._move_video()

    def _update_origin_dir(self):
        self.origin_dir = self.video.get_root()

    def _update_target_file_path(self):
        self.target_subdir = generate_destination_path(self.video, self.target_root, self.format_string)
        self.target_file_path = self.target_subdir / self.video.get_filename()

    def _make_dirs(self):
        self.created_dirs = fileutils.make_dirs(self.target_subdir)

    def _move_video(self):
        fileutils.move_file(self.video.get_path(), self.target_subdir, False)
        self.video.update_file_data(self.target_subdir / self.video.get_filename(), True)

    def undo(self):
        self._undo_move_video()
        self._undo_make_dirs()

    def _undo_move_video(self):
        dest_path = self.origin_dir / self.video.get_filename()
        fileutils.move_file(self.video.get_path(), dest_path)

    def _undo_make_dirs(self):
        fileutils.remove_dirs(self.created_dirs)

    def validate_exec(self) -> tuple[bool, list[str]]:
        self._update_target_file_path()
        return fileutils.validate_move(self.video.get_path(), self.target_file_path)

    def validate_undo(self) -> tuple[bool, list[str]]:
        current_path = self.video.get_path()
        origin_path = self.origin_dir / self.video.get_filename()
        return fileutils.validate_move(current_path, origin_path)
