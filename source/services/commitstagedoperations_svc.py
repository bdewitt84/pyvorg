# ./source/services/commitstagedoperations_svc.py

# Standard library
# n/a

# Local imports
from source.commands.cmdbuffer import CommandBuffer
from source.state.application_state import PyvorgState
from source.utils import \
    cmdutils

# Third-party packages
# n/a


class CommitStagedOperations:
    def __init__(self):
        pass

    def call(self,
             state: PyvorgState):
        cmdutils.execute_cmd_buffer(state.command_buffer)
        state.batch_history.append(state.command_buffer)
        state.command_buffer = CommandBuffer()
