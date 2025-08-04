# ./source/services/clearstagedoperations_svc.py

# Standard library
# n/a

# Local imports
from source.commands.cmdbuffer import CommandBuffer
from source.utils import \
    cmdutils

# Third-party packages
# n/a


class ClearStagedOperations:
    def __init__(self):
        pass

    def call(self, command_buffer: CommandBuffer):
        cmdutils.clear_exec_buffer(command_buffer)
