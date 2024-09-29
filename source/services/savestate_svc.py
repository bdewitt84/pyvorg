# ./source/services/savestate_svc.py

# Standard library

# Local imports
from source.state.application_state import PyvorgState
from source.utils import \
    configutils, \
    fileutils, \
    serializeutils

# Third party packages
# n/a


class SaveState:
    def __init__(self):
        pass

    def call(self, state: PyvorgState):
        jar_path = configutils.get_default_state_path()
        serialized_state = serializeutils.obj_to_pickle(state)
        fileutils.file_write_bytes(jar_path, serialized_state, overwrite=True)
