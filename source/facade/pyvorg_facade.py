# ./source/facade/pyvorg_facade.py

"""
    Acts as entry point for user interface.
    Should only interact with the services layer.
"""

# Standard library
from pathlib import Path
from typing import Optional

# Local imports
from source.state.application_state import PyvorgState
from source.utils import serializeutils as serial_svc
from source.utils import fileutils as file_svc
from source.utils import configutils as cfg_svc
from source.utils import cmdutils as cmd_svc


# Third-party packages
# n\a


# TODO: We'll refactor MediaFile to be any arbitrary media file.
#       Maybe use MediaFile as a base, with MediaFile and Subtitle as subclasses
#       when we scan we can add media files to the collection based on file extension
#       consider simply adding 'type:value' key value pair to file info
#       then we can easily apply filters


class Facade:
    def __init__(self, state: PyvorgState = None):
        # TODO: need to implement members as a state object in order to
        #       implement load_state() and save_state() as a service
        #       currently, we have to pass
        self.state = state or PyvorgState()
        # self.collection = collection
        # self.command_buffer = command_buffer
        # self.command_buffer_history: list[command_buffer] = []

    def clear_staged_operations(self) -> None:
        from source.services.clearstagedoperations_svc import ClearStagedOperations
        ClearStagedOperations().call(self.state.get_command_buffer())

    def commit_staged_operations(self) -> None:
        # TODO: Implement state first
        cmd_svc.execute_cmd_buffer(self.state.get_command_buffer())
        self.state.get_batch_history().append(self.state.get_command_buffer())
        self.state.clear_command_buffer()

    def export_collection_metadata(self, path: str) -> None:
        from source.services.exportcollectionmetadata_svc import ExportCollectionMetadata
        ExportCollectionMetadata().call(self.state.get_collection(),
                                        path)

    def get_preview_of_staged_operations(self) -> str:
        # TODO: Figure out what to do with this one
        return cmd_svc.get_exec_preview(self.state.get_command_buffer())

    def import_collection_metadata(self, path: Path) -> None:
        from source.services.importcollectionmetadata_svc import ImportCollectionMetadata
        ImportCollectionMetadata().call(self.state.get_collection(), path)

    def scan_files_in_path(self,
                           path_string: str,
                           recursive: bool = False) -> None:

        from source.services.scanfilesinpath_svc import ScanFilesInPath
        ScanFilesInPath().call(self.state.get_collection(),
                               path_string,
                               recursive)

    def save_state(self):
        # TODO: Implement state first
        # jar = PyvorgState(self.collection,
        #                   self.command_buffer,
        #                   self.command_buffer_history)
        jar_path = cfg_svc.get_default_state_path()
        serialized_state = serial_svc.obj_to_pickle(self.state)
        file_svc.file_write_bytes(jar_path, serialized_state, overwrite=True)

    def load_state(self):
        from source.services.loadstate_svc import LoadState
        LoadState().call(self.state)

    def stage_organize_video_files(self,
                                   destination: Optional[str] = None,
                                   format_str: Optional[str] = None,
                                   filter_strings: Optional[list[str]] = None) -> None:

        from source.services.stageorganizevideofiles_svc import StageOrganizeVideoFiles
        StageOrganizeVideoFiles().call(self.state.get_collection(),
                                       self.state.get_command_buffer(),
                                       destination,
                                       format_str,
                                       filter_strings)

    def stage_update_api_metadata(self,
                                  api_name: str,
                                  filter_strings: Optional[list[str]] = None) -> None:

        from source.services.stageupdatemetadata_svc import StageUpdateMetadata
        StageUpdateMetadata().call(self.state.get_collection(),
                                   self.state.get_command_buffer(),
                                   api_name,
                                   filter_strings)

    def undo_transaction(self) -> None:
        from source.services.undotransaction_svc import UndoTransaction
        UndoTransaction().call(self.state.get_batch_history())
