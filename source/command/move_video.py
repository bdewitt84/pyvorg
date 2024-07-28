# source/command/move_video.py

"""
    Implementation of MoveVideo command used by CommandBuffer
"""

# Standard library
import os
import json
import logging

# Local imports
from source.command.command import Command
from source.utils.helper import make_dir, move_file

# Third-party packages


class MoveVideo(Command):
    def __init__(self, video, dest_dir):
        self.video = video
        self.dest_dir = dest_dir
        self.undo_dir = None
        self.created_dirs = []

    def exec(self):
        self.undo_dir = self.video.get_path()
        self._move(self.dest_dir)

    @staticmethod
    def from_dict(d):
        new = MoveVideo(None, None)
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
        self._move(self.undo_dir)
        # remove any directories that needed to be created
        for dir in self.created_dirs:
            if os.path.exists(dir) and len(os.listdir(dir)) == 0:
                os.rmdir(dir)
            else:
                logging.info(f"Directory '{dir}' does not exist or is not empty")

    def _move(self, dest_dir):
        self._make_dirs(dest_dir)
        dest_path = os.path.join(dest_dir, self.video.get_filename())
        move_file(self.video.get_path(), dest_path)
        self.video.update_file_data(dest_path)

    def _make_dirs(self, dest_dir):
        while dest_dir and not os.path.dirname(dest_dir):
            self.created_dirs.append(dest_dir)
            dest_dir = os.path.dirname(dest_dir)

        for dir in reversed(self.created_dirs):
            make_dir(dir)

    def _validate_move(self, src_path, dst_path):
        err = []
        dest_dir = os.path.dirname(dst_path)

        # Check the source exists
        if not os.path.exists(src_path):
            err.append(f"The source '{src_path}' does not exist\n")
        # Check the destination does not exist
        if os.path.exists(dst_path):
            err.append(f"The destination '{dst_path}' already exists.")
        # Check read permission of the source
        if not os.access(src_path, os.R_OK):
            err.append(f"No permission to read from source '{src_path}'")
        # Check write permission of the source
        if not os.access(src_path, os.W_OK):
            err.append(f"No permission to write to source '{src_path}'")
        # Check permission to write to the destination
        if not os.access(dest_dir, os.W_OK):
            err.append(f"No permission to write to destination '{dest_dir}'")

        valid = True if len(err) == 0 else False
        return valid, err

    def validate_exec(self):
        dest_path = os.path.join(self.dest_dir, self.video.get_filename())
        return self._validate_move(self.video.get_path(), dest_path)

    def validate_undo(self):
        dest_path = os.path.join(self.undo_dir, self.video.get_filename())
        return self._validate_move(self.video.get_path(), dest_path)

    def __str__(self):
        return f"Move \t{self.video.get_path()} \nto \t\t{self.dest_dir}\n"
