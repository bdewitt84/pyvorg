# source/command/move_video.py

"""
    Implementation of MoveVideo command used by CommandBuffer
"""

# Standard library
import os
from pathlib import Path
import json
import logging

# Local imports
from source.state.command import Command
from service.file_svc import \
    dir_is_empty, \
    make_dir, \
    move_file, \
    path_is_readable, \
    path_is_writable

# Third-party packages


class MoveVideo(Command):
    def __init__(self, video, dest_dir: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video = video
        self.dest_dir = dest_dir
        self.origin_dir = None
        self.created_dirs = []

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.dest_dir}\n"

    def exec(self):
        self.origin_dir = self.video.get_root()
        self._move(self.dest_dir)

    def to_dict(self):
        output_dict = {
            'video': self.video.to_dict(),
            'dest_dir': self.dest_dir,
            'origin_dir': self.origin_dir,
            'created_dirs': self.created_dirs
        }
        return output_dict

    def undo(self):
        self._move(self.origin_dir)
        self._undo_make_dirs()

    def validate_exec(self):
        src_path = self.video.get_path()
        dest_path = Path(self.dest_dir) / self.video.get_filename()
        return self._validate_move(src_path, dest_path)

    def validate_undo(self):
        current_path = self.video.get_path()
        origin_path = Path(self.origin_dir, self.video.get_filename())
        return self._validate_move(current_path, origin_path)

    def _make_dirs(self, dest_dir: Path):
        # TODO: Can be refactored into two functions
        while not dest_dir.exists():
            self.created_dirs.append(dest_dir)
            dest_dir = dest_dir.parent

        for directory in reversed(self.created_dirs):
            make_dir(directory)

    def _move(self, dest_dir: Path):
        self._make_dirs(dest_dir.resolve())
        if not dest_dir.exists():
            raise FileNotFoundError(f"path '{dest_dir}' could not be created")
        dest_path = Path(dest_dir) / self.video.get_filename()
        move_file(self.video.get_path(), dest_path)
        self.video.update_file_data(dest_path)

    def _undo_make_dirs(self):
        for directory in self.created_dirs:
            if directory.exists() and dir_is_empty(directory):
                directory.rmdir()
            else:
                logging.info(f"Cannot remove directory: '{directory}' does not exist or is not empty")

    @staticmethod
    def _validate_move(src_path: Path, dest_path: Path):
        err = []

        if not src_path.exists():
            err.append(f"The source '{src_path}' does not exist\n")

        if not dest_path.exists():
            err.append(f"The destination '{dest_path}' already exists.")

        if not path_is_readable(src_path):
            err.append(f"No permission to read from source '{src_path}'")

        if not path_is_writable(src_path):
            err.append(f"No permission to write to source '{src_path}'")

        if not path_is_writable(dest_path.parent):
            err.append(f"No permission to write to destination '{dest_path.parent}'")

        return len(err) == 0, err
