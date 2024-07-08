# source/command.py

"""
Command base class and derived classes providing functions for use
in the command buffer via the collection class, which include moving
videos and creating directories.
"""

# Standard library
import logging
import os
import shutil

# Local imports
from source.constants import *
from source.helper import make_dir
from source.helper import move_file
from source.helper import remove_empty_dir
from source.exceptions import ValidationError


class Command:
    def validate_exec(self):
        raise NotImplementedError

    def validate_undo(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


# class MoveVideo(Command):
#     # TODO: Add logging
#     #       Consider changing ValidationError to MoveCommandValidationError, or something similar.
#     def __init__(self, video, dest_dir):
#         self.video = video
#         self.dest_dir = dest_dir
#         self.src_file_path = video.get_path()
#         self.src_dir, self.filename = os.path.split(self.src_file_path)
#         self.dest_file_path = os.path.join(dest_dir, self.filename)
#         self.undo_path = None
#
#     def validate_exec(self):
#         self._validate_file_not_exist(self.dest_file_path)
#         self._validate_file_exists(self.src_file_path)
#         self._validate_path_not_changed(self.src_file_path)
#
#     def validate_undo(self):
#         self._validate_file_not_exist(self.src_file_path)
#         self._validate_file_exists(self.dest_file_path)
#         self._validate_path_not_changed(self.dest_file_path)
#
#     def _validate_file_not_exist(self, path):
#         if os.path.exists(path):
#             msg = f'Cannot move file; dest {path} already exists.'
#             raise ValidationError(msg)
#
#     def _validate_file_exists(self, path):
#         if not os.path.exists(path):
#             msg = f'Cannot move file; {path} does not exist.'
#             raise ValidationError(msg)
#
#     def _validate_path_not_changed(self, path):
#         # Check if the current file path in the metadata has changed since it entered the history buffer
#         current_file_path = self.video.get_path()
#         if path != current_file_path:
#             msg = f'Path of file {self.filename} has changed since this command entered the command queue/undo stack.'
#             raise ValidationError(msg)
#
#     def execute(self):
#         self.undo_path = self.video.get_path()
#         self._move_video(self.dest_dir)
#
#     def undo(self):
#         self._move_video(self.src_dir)
#
#     def _move_video(self, dest_dir):
#         current_file_path = self.video.get_path()
#         dest_file_path = os.path.join(dest_dir, self.video.get_filename())
#
#         shutil.move(current_file_path, dest_dir)
#         self.video.update_file_data(dest_file_path)
#
#         logging.info('Moved {} \n to {}'.format(current_file_path, dest_dir))
#
#     def __str__(self):
#         return "Move {} to {}".format(self.video.get_path(), self.dest_dir)


# class CreateVideoDirectory(Command):
#
#     def __init__(self, video, path):
#         self.video = video
#         self.path = path
#         self.dir = None
#         self.path_exists = os.path.exists(path)
#
#     def execute(self):
#         # make_dir(self.path)
#         pass
#
#     def validate_exec(self):
#         self._validate_path_changed()
#         return
#
#     # Todo: Do we care about this? Why is it important if the file moved as long as we know where it is now? The move
#     #       command should update the last known path. That should be the undo path.
#     def _validate_path_changed(self):
#         if self.path != self.video.get_path():
#             raise ValidationError(f"The path of '{self.video.get_filename()}' has changed to .")
#
#     def validate_undo(self):
#         self._validate_path_exists()
#         self._validate_dir_not_empty()
#
#     def _validate_path_exists(self):
#         if not os.path.exists(self.path):
#             raise ValidationError(f"'{self.path}' does not exist.")
#
#     def _validate_dir_not_empty(self):
#         if len(os.listdir(self.path)) != 0:
#             raise ValidationError(f"'{self.path}' is not empty")
#
#     def undo(self):
#         if msg := self.validate_undo():
#             os.rmdir(self.dir)
#         else:
#             raise ValidationError(msg)
#
#     def generate_dir_name(self, format='%title (%year)'):
#         name = format
#         for spec, (key, default) in FORMAT_SPECIFIERS.items():
#             data = self.get_data(key, default)
#             name = name.replace(spec, str(data))
#         return name
#
#     def __str__(self):
#         return "Create directory {}".format(self.path)


class RemoveEmptyDir(Command):
    def __init__(self, path):
        self.path = path

    def validate_exec(self):
        msg = ""
        if not os.path.exists(self.path):
            msg = f"Cannot remove {self.path}, directory does not exist."
        elif os.listdir(self.path) == 0:
            msg = f"Cannot remove {self.path}, directory is not empty."
        return msg

    def validate_undo(self):
        msg = ""
        if os.path.exists(self.path):
            msg = f"Cannot undo removal of {self.path}, directory already exists."
        return msg

    def execute(self):
        if msg := self.validate_exec():
            remove_empty_dir(self.path)
        else:
            raise ValidationError(msg)

    def undo(self):
        if msg := self.validate_undo():
            os.mkdir(self.path)
        else:
            raise ValidationError(msg)

    def __str__(self):
        return "Remove {} if empty\n".format(self.path)


class MoveVideo(Command):
    def __init__(self, video, dest_dir):
        self.video = video
        self.dest_dir = dest_dir
        self.undo_dir = None
        self.created_dirs = []

    def execute(self):
        self.undo_dir = self.video.get_path()
        self._move(self.dest_dir)

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

    def validate_exec(self):
        pass

    def validate_undo(self):
        pass
