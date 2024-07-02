# source/combuffer.py

"""
Command buffer implementation used by Collection to enable batching
of processes and related functions, such as load, save, undo, etc.
"""

# Standard library
import pickle
from queue import Queue

# Local imports
from .command import *


class CommandBuffer:
    def __init__(self):
        self.cmd_buffer = Queue()
        self.undo_buffer = []

    def add_command(self, cmd: Command):
        if isinstance(cmd, Command):
            self.cmd_buffer.put(cmd)
        else:
            raise ValueError("Only objects with type <Command> may be added to the command buffer.")

    def add_create_video_dir(self, video, dest):
        self.add_command(CreateVideoDirectory(video, dest))

    def add_move_video(self, video, dest):
        self.add_command(MoveVideo(video, dest))

    def exec_command(self):
        cmd = self.cmd_buffer.get()
        cmd.execute()
        self.undo_buffer.append(cmd)

    def undo_cmd(self):
        if self.undo_buffer:
            cmd = self.undo_buffer.pop()
            cmd.undo()
        else:
            raise IndexError("Cannot undo; command history is empty")

    def validate_exec_buffer(self):
        if self.cmd_buffer:
            for cmd in self.cmd_buffer.queue:
                cmd.validate_exec()
        else:
            print('Nothing to validate, exec_buffer is empty.\n')

    def validate_undo_buffer(self):
        if self.undo_buffer:
            for cmd in self.undo_buffer:
                cmd.validate_undo()
        else:
            print('Nothing to validate, undo_buffer is empty.\n')

    def execute_cmd_buffer(self):
        if self.cmd_buffer:
            while not self.cmd_buffer.empty():
                try:
                    self.exec_command()
                except ValidationError as e:
                    logging.error(e)
                    break
        else:
            raise IndexError("Cannot execute; command buffer is empty.\n")

    def execute_undo_buffer(self):
        if self.undo_buffer:
            while self.undo_buffer:
                try:
                    self.exec_command()
                except ValidationError as e:
                    logging.error(e)
                    break
        else:
            raise IndexError("Cannot undi; undo buffer is empty.\n")

    def preview_buffer(self):
        for cmd in self.cmd_buffer.queue:
            print(cmd)

    def save_buffer(self, path='./command_buffer.sav'):
        # TODO: add empty buffer check to unit test
        if self.cmd_buffer.queue or self.undo_buffer:
            jar = {'buffer': self.cmd_buffer.queue,
                   'history': self.undo_buffer}
            with open(path, 'wb') as file:
                pickle.dump(jar, file)

    def load_buffer(self, path='./command_buffer.sav'):
        with open(path, 'rb') as file:
            jar = pickle.load(file)
        self.cmd_buffer.queue = jar.get('buffer')
        self.undo_buffer = jar.get('history')

    def __str__(self):
        ret = ''
        if self.cmd_buffer.queue:
            for cmd in self.cmd_buffer.queue:
                ret += str(cmd) + '\n'
        else:
            ret = "Command buffer is empty."

        return ret