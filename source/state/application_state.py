# ./source/state/application_state.py

# Standard library
from typing import Optional

# Local Imports
from source.state.col import Collection
from source.state.cmdbuffer import CommandBuffer

# Third-party packages
# n/a


class PickleJar:
    def __init__(self, collection: Optional[Collection] = None,
                 command_buffer: Optional[CommandBuffer] = None,
                 batch_history: Optional[list[CommandBuffer]] = None):
        self.collection = collection or Collection()
        self.command_buffer = command_buffer or CommandBuffer()
        self.batch_history = batch_history or []
