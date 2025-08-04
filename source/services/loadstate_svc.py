# ./source/services/loadstate_svc.py

# Standard library

# Local imports
from source.state.application_state import PyvorgState
from source.utils import \
    configutils, \
    fileutils, \
    serializeutils

# Third party packages
# n/a


class LoadState:
    def __init__(self):
        pass

    def call(self,
             state: PyvorgState):
        pickle_path = configutils.get_default_state_path()
        serialized_state = fileutils.file_read_bytes(pickle_path)
        loaded_state = serializeutils.pickle_to_object(serialized_state) or PyvorgState()
        state.collection = loaded_state.collection
        state.command_buffer = loaded_state.command_buffer
        state.batch_history = loaded_state.batch_history
