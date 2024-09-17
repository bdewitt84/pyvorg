# source/combuffer.py

"""
    Command buffer implementation used by Collection to enable batching
    of processes and related functions, such as load, save, undo, etc.
"""

# Standard library
from collections import deque

# Local imports
from source.state.command import Command

# Third-party packages


class CommandBuffer:
    def __init__(self):
        self.cmd_buffer = deque()
        self.undo_buffer = []

    def add_command(self, cmd: Command) -> None:
        if not isinstance(cmd, Command):
            raise ValueError("Only objects with type <Command> may be added to the command buffer.")
        self.cmd_buffer.append(cmd)

    def clear_exec_buffer(self):
        self.cmd_buffer.clear()

    def clear_undo_buffer(self):
        self.undo_buffer.clear()

    def execute_cmd_buffer(self):
        if not self.cmd_buffer:
            raise IndexError("Cannot execute; command buffer is empty.\n")
        while self.cmd_buffer:
            self.exec_command()

    def exec_command(self):
        if not self.cmd_buffer:
            raise IndexError("No commands in buffer to execute")
        cmd = self.cmd_buffer.popleft()
        cmd.exec()
        self.undo_buffer.append(cmd)

    def exec_is_empty(self) -> bool:
        return not bool(len(self.cmd_buffer))

    def execute_undo_buffer(self):
        if not self.undo_buffer:
            raise IndexError("Cannot undo; undo buffer is empty.\n")
        while self.undo_buffer:
            self.undo_cmd()

    def from_dict(self):
        # TODO: implement
        pass

    def _get_commands(self):
        return [cmd for cmd in self.cmd_buffer]

    def preview_buffer(self):
        return str(self)

    def undo_cmd(self):
        if not self.undo_buffer:
            raise IndexError("Cannot undo; command history is empty")
        cmd = self.undo_buffer.pop()
        cmd.undo()

    # TODO: Generate list of errors, present it to user
    def validate_exec_buffer(self):
        if self.cmd_buffer:
            for cmd in self.cmd_buffer:
                cmd.validate_exec()
        else:
            print('Nothing to validate, exec_buffer is empty.\n')

    # TODO: Generate list of errors, present it to user
    def validate_undo_buffer(self):
        if self.undo_buffer:
            for cmd in self.undo_buffer:
                cmd.validate_undo()
        else:
            print('Nothing to validate, undo_buffer is empty.\n')

    def to_dict(self):
        # TODO: Implement
        pass

    def __str__(self):
        ret = ''
        if self.cmd_buffer:
            for cmd in self.cmd_buffer:
                ret += str(cmd) + '\n'
        else:
            ret = "Command buffer is empty."

        return ret
