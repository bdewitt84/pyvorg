# ./source/services/undotransaction_svc.py

# Standard library

# Local imports
from source.utils import \
    cmdutils


# Third party packages
# n/a


class UndoTransaction:
    def __init__(self):
        pass

    def call(self, command_buffer_history):
        if command_buffer_history:
            batch = command_buffer_history.pop()
            cmdutils.execute_undo_buffer(batch)
