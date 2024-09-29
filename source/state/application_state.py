# ./source/state/application_state.py

# Standard library
from typing import Optional

# Local Imports
from source.state.col import Collection
from source.commands.cmdbuffer import CommandBuffer

# Third-party packages
# n/a


class PyvorgState:
    def __init__(self, collection: Optional[Collection] = None,
                 command_buffer: Optional[CommandBuffer] = None,
                 batch_history: Optional[list[CommandBuffer]] = None):
        self.collection = collection or Collection()
        self.command_buffer = command_buffer or CommandBuffer()
        self.batch_history = batch_history or []

    def get_collection(self):
        return self.collection

    def get_command_buffer(self):
        return self.command_buffer

    def clear_command_buffer(self):
        self.command_buffer = CommandBuffer()

    def get_batch_history(self):
        return self.batch_history
