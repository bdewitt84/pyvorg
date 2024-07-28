# source/combuffer.py

"""
    Command buffer implementation used by Collection to enable batching
    of processes and related functions, such as load, save, undo, etc.
"""

# Standard library
import logging
import pickle
# from queue import Queue
from collections import deque

# Local imports
from source.command.command import Command
# from source.command.move_video import MoveVideo
from source.exceptions import ValidationError

# Third-party packages


class CommandBuffer:
    def __init__(self):
        # self.cmd_buffer = Queue()
        self.cmd_buffer = deque()
        self.undo_buffer = []

    def add_command(self, cmd: Command):
        if isinstance(cmd, Command):
            # self.cmd_buffer.put(cmd)
            self.cmd_buffer.append(cmd)
        else:
            raise ValueError("Only objects with type <Command> may be added to the command buffer.")

    def exec_command(self):
        # cmd = self.cmd_buffer.get()
        cmd = self.cmd_buffer.popleft()
        cmd.exec()
        self.undo_buffer.append(cmd)

    def from_dict(self):
        # TODO: implement
        pass

    def from_json(self):
        # TODO: implement
        pass

    def undo_cmd(self):
        if self.undo_buffer:
            cmd = self.undo_buffer.pop()
            cmd.undo()
        else:
            raise IndexError("Cannot undo; command history is empty")

    # Todo: Generate list of errors, present it to user
    def validate_exec_buffer(self):
        if self.cmd_buffer:
            for cmd in self.cmd_buffer:
                cmd.validate_exec()
        else:
            print('Nothing to validate, exec_buffer is empty.\n')

    # Todo: Generate list of errors, present it to user
    def validate_undo_buffer(self):
        if self.undo_buffer:
            for cmd in self.undo_buffer:
                cmd.validate_undo()
        else:
            print('Nothing to validate, undo_buffer is empty.\n')

    def execute_cmd_buffer(self):
        if self.cmd_buffer:
            while self.cmd_buffer:
                self.exec_command()
        else:
            raise IndexError("Cannot execute; command buffer is empty.\n")

    def execute_undo_buffer(self):
        if self.undo_buffer:
            while self.undo_buffer:
                self.undo_cmd()
        else:
            raise IndexError("Cannot undo; undo buffer is empty.\n")

    def preview_buffer(self):
        for cmd in self.cmd_buffer:
            print(cmd)

    # def save_buffer(self, path='./command_buffer.sav'):
    #     if self.cmd_buffer.queue or self.undo_buffer:
    #         jar = {'buffer': self.cmd_buffer.queue,
    #                'history': self.undo_buffer}
    #         with open(path, 'wb') as file:
    #             pickle.dump(jar, file)
    #     else:
    #         # Buffer is empty
    #         pass

    def to_dict(self):
        # TODO: Implement
        pass

    def to_json(self):
        # TODO: Implement
        pass

    # def load_buffer(self, path='./command_buffer.sav'):
    #     with open(path, 'rb') as file:
    #         jar = pickle.load(file)
    #     self.cmd_buffer.queue = jar.get('buffer')
    #     self.undo_buffer = jar.get('history')

    def __str__(self):
        ret = ''
        if self.cmd_buffer:
            for cmd in self.cmd_buffer:
                ret += str(cmd) + '\n'
        else:
            ret = "Command buffer is empty."

        return ret
