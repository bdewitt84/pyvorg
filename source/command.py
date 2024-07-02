import logging
import os
import shutil
from .helper import make_dir
from .helper import remove_empty_dir
from .exceptions import ValidationError


class Command:
    def validate_exec(self):
        raise NotImplementedError

    def validate_undo(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


class MoveVideo(Command):
    # TODO: Add logging
    #       Consider changing ValidationError to MoveCommandValidationError, or something similar.
    def __init__(self, video, dest_dir):
        self.video = video
        self.dest_dir = dest_dir
        self.src_file_path = video.get_path()
        self.src_dir, self.filename = os.path.split(self.src_file_path)
        self.dest_file_path = os.path.join(dest_dir, self.filename)

    def validate_exec(self):
        self._validate_file_not_exist(self.dest_file_path)
        self._validate_file_exists(self.src_file_path)
        self._validate_path_not_changed(self.src_file_path)

    def validate_undo(self):
        self._validate_file_not_exist(self.src_file_path)
        self._validate_file_exists(self.dest_file_path)
        self._validate_path_not_changed(self.dest_file_path)

    def _validate_file_not_exist(self, path):
        # Check that the undo won't overwrite an existing file
        if os.path.exists(path):
            msg = f'Cannot move file; dest {path} already exists.'
            raise ValidationError(msg)

    def _validate_file_exists(self, path):
        # Check that the file we want to un-move still exists at the expected path
        if not os.path.exists(path):
            msg = f'Cannot move file; {path} does not exist.'
            raise ValidationError(msg)

    def _validate_path_not_changed(self, path):
        # Check if the current file path in the metadata has changed since it entered the history buffer
        current_file_path = self.video.get_path()
        if path != current_file_path:
            msg = f'Path of file {self.filename} has changed since this command entered the command queue/undo stack.'
            raise ValidationError(msg)

    def execute(self):
        self._move_video(self.dest_dir)

    def undo(self):
        self._move_video(self.src_dir)

    def _move_video(self, dest_dir):
        current_full_path = self.video.get_path()
        dest_full_path = os.path.join(dest_dir, self.video.get_filename())

        shutil.move(current_full_path, dest_dir)
        self.video.update_file_data(dest_full_path)

        logging.info('Moved {} \n to {}'.format(current_full_path, dest_dir))

    def __str__(self):
        return "Move {} to {}".format(self.video.get_path(), self.dest_dir)


class CreateVideoDirectory(Command):

    # TODO: refactor the dir name generation into this command.
    def __init__(self, video, path):
        self.video = video
        self.path = path
        self.dir = None

    def execute(self):
        if msg := self.validate_exec():
            make_dir(self.path)
        else:
            raise ValidationError(msg)

    def validate_exec(self):
        msg = ""
        if self.path != self.video.generate_dir_name(self.video, self.path):
            msg = f"Video videos for {self.video.get_filename()} has changed since this command was added to the " \
                  f"command buffer. "
        elif os.path.exists(self.path):
            msg = f"Cannot create directory, {self.path} already exists."
        return msg

    def validate_undo(self):
        msg = ""
        if not os.path.exists(self.path):
            msg = f"Cannot undo creation of {self.path}, does not exist."
        elif os.listdir(self.path) == 0:
            msg = f"Cannot undo creation of {self.path}, directory is not empty."
        return msg

    def undo(self):
        if msg := self.validate_undo():
            os.rmdir(self.dir)
        else:
            raise ValidationError(msg)

    def __str__(self):
        return "Create directory {}".format(self.path)


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