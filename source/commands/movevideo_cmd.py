# source/command/movevideo_cmd.py

"""
Implementation of MoveVideoCmd command used by CommandBuffer
"""

# Standard library
from pathlib import Path

# Local imports
import source.service.fileutils as file_svc
from source.commands.command_base import Command
from source.state.mediafile import MediaFile
from source.service.videoutils import generate_destination_path

# Third-party packages


# TODO: Refactor to move_media_file.py


class MoveVideoCmd(Command):
    def __init__(self,
                 video: MediaFile,
                 dest_dir: Path,
                 format_string: str,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.video = video
        self.dest_dir = dest_dir.resolve()
        self.format_string = format_string
        self.origin_dir = None
        self.created_dirs = []

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.dest_dir}\n"

    def exec(self) -> None:
        self._update_source_root()
        self._generate_destination_dir_name()
        self._make_dirs()
        self._move_video()

    def undo(self):
        self._undo_move_video()
        self._undo_make_dirs()

    def validate_exec(self) -> tuple[bool, list[str]]:
        src_path = self.video.get_path()
        dest_path = Path(self.dest_dir) / self.video.get_filename()
        return file_svc.validate_move(src_path, dest_path)

    def validate_undo(self) -> tuple[bool, list[str]]:
        current_path = self.video.get_path()
        origin_path = Path(self.origin_dir, self.video.get_filename())
        return file_svc.validate_move(current_path, origin_path)

    def _move_video(self):
        self.created_dirs = file_svc.make_dirs(self.dest_dir)
        file_svc.move_file(self.video.get_path(), self.dest_path, False)
        self.video.update_file_data(self.dest_path / self.video.get_filename(), True)

    def _update_source_root(self):
        self.origin_dir = self.video.get_root()

    def _generate_destination_dir_name(self):
        self.dest_path = generate_destination_path(self.video, self.dest_dir, self.format_string)

    def _make_dirs(self):
        self.created_dirs = file_svc.make_dirs(self.dest_path)

    def _undo_move_video(self):
        dest_path = self.origin_dir / self.video.get_filename()
        file_svc.move_file(self.video.get_path(), dest_path)

    def _undo_make_dirs(self):
        file_svc.remove_dirs(self.created_dirs)
