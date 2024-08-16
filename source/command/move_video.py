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
from source.command.command import Command
from source.utils.helper import \
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

    @staticmethod
    def from_dict(d):
        new = MoveVideo(None, Path())
        new.__dict__ = d
        new.video = d.get('video')
        return new

    @staticmethod
    def from_json(j):
        serialized = json.loads(j)
        return MoveVideo.from_dict(serialized)

    def to_dict(self):
        d = self.__dict__
        d.update({'video': self.video.to_dict()})
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

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
        while dest_dir and not os.path.dirname(dest_dir):
            self.created_dirs.append(dest_dir)
            dest_dir = os.path.dirname(dest_dir)

        for directory in reversed(self.created_dirs):
            make_dir(directory)

    def _move(self, dest_dir: Path):
        self._make_dirs(dest_dir)
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
