# source/command/movevideo_cmd.py

"""
Implementation of MoveVideo command used by CommandBuffer
"""

# Standard library
from pathlib import Path

# Local imports
import source.service.file_svc as file_svc
import source.service.video_svc as video_svc
from source.state.command_base import Command
from source.state.mediafile import MediaFile

# Third-party packages


# TODO: Refactor to move_media_file.py


class MoveVideo(Command):
    def __init__(self, video: MediaFile, dest_dir: Path, format_string: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video = video
        self.dest_dir = dest_dir.resolve()
        self.format_string = format_string
        self.origin_dir = None
        self.created_dirs = []

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.dest_dir}\n"

    def exec(self) -> None:
        dest_dir = video_svc.generate_destination_path(self.video, self.dest_dir, self.format_string)
        dest_path = dest_dir / self.video.get_filename()
        self._update_undo_data(self.video.get_root(), file_svc.make_dirs(dest_dir))
        file_svc.move_file(self.video.get_path(), dest_path)
        self.video.update_file_data(dest_path, skip_hash=True)

    def _update_undo_data(self, origin_dir: Path, created_dirs: list[Path]):
        self.origin_dir = origin_dir
        self.created_dirs = created_dirs

    def to_dict(self) -> dict:
        output_dict = {
            'video': self.video.to_dict(),
            'dest_dir': self.dest_dir,
            'origin_dir': self.origin_dir,
            'created_dirs': self.created_dirs
        }
        return output_dict

    def undo(self):
        dest_path = self.origin_dir / self.video.get_filename()
        file_svc.move_file(self.video.get_path(), dest_path)
        file_svc.remove_dirs(self.created_dirs)

    def validate_exec(self) -> tuple[bool, list[str]]:
        src_path = self.video.get_path()
        dest_path = Path(self.dest_dir) / self.video.get_filename()
        return file_svc.validate_move(src_path, dest_path)

    def validate_undo(self) -> tuple[bool, list[str]]:
        current_path = self.video.get_path()
        origin_path = Path(self.origin_dir, self.video.get_filename())
        return file_svc.validate_move(current_path, origin_path)
