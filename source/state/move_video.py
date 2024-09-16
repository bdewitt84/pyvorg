# source/command/move_video.py

"""
Implementation of MoveVideo command used by CommandBuffer
"""

# Standard library
from pathlib import Path

# Local imports
from source.state.command import Command
import source.service.file_svc as file_svc

# Third-party packages


# TODO: Refactor to move_media_file.py


class MoveVideo(Command):
    def __init__(self, video, dest_dir: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video = video
        self.dest_dir = dest_dir.resolve()
        self.origin_dir = None
        self.created_dirs = []

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.dest_dir}\n"

    def exec(self):
        # Create undo information
        self.origin_dir = self.video.get_root()
        self.created_dirs = file_svc.make_dirs(self.dest_dir)

        # Perform the move
        dest_path = self.dest_dir / self.video.get_filename()
        file_svc.move_file(self.video.get_path(), dest_path)

        # Update metadata
        self.video.update_file_data(dest_path, skip_hash=True)

    def to_dict(self):
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

    def validate_exec(self):
        src_path = self.video.get_path()
        dest_path = Path(self.dest_dir) / self.video.get_filename()
        return self._validate_move(src_path, dest_path)

    def validate_undo(self):
        current_path = self.video.get_path()
        origin_path = Path(self.origin_dir, self.video.get_filename())
        return self._validate_move(current_path, origin_path)

    @staticmethod
    def _validate_move(src_path: Path, dest_path: Path):
        err = []

        if not src_path.exists():
            err.append(f"The source '{src_path}' does not exist\n")

        if not dest_path.exists():
            err.append(f"The destination '{dest_path}' already exists.")

        if not file_svc.path_is_readable(src_path):
            err.append(f"No permission to read from source '{src_path}'")

        if not file_svc.path_is_writable(src_path):
            err.append(f"No permission to write to source '{src_path}'")

        if not file_svc.path_is_writable(dest_path.parent):
            err.append(f"No permission to write to destination '{dest_path.parent}'")

        return len(err) == 0, err
