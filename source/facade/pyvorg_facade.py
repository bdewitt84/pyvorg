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
from source.utils import cmdutils as cmd_svc
from source.services.clearstagedoperations_svc import ClearStagedOperations
from source.services.commitstagedoperations_svc import CommitStagedOperations
from source.services.exportcollectionmetadata_svc import ExportCollectionMetadata
from source.services.importcollectionmetadata_svc import ImportCollectionMetadata
from source.services.savestate_svc import SaveState
from source.services.loadstate_svc import LoadState
from source.services.stageorganizevideofiles_svc import StageOrganizeVideoFiles
from source.services.stageupdatemetadata_svc import StageUpdateMetadata
from source.services.undotransaction_svc import UndoTransaction


# Third-party packages
# n\a


# TODO: We'll refactor MediaFile to be any arbitrary media file.
#       Maybe use MediaFile as a base, with MediaFile and Subtitle as subclasses
#       when we scan we can add media files to the collection based on file extension
#       consider simply adding 'type:value' key value pair to file info
#       then we can easily apply filters


class Facade:
    def __init__(self, state: PyvorgState = None):
        self.state = state or PyvorgState()

    def clear_staged_operations(self) -> None:
        ClearStagedOperations().call(self.state.get_command_buffer())

    def commit_staged_operations(self) -> None:
        CommitStagedOperations().call(self.state)

    def export_collection_metadata(self, path: str) -> None:
        ExportCollectionMetadata().call(self.state.get_collection(),
                                        path)

    def get_preview_of_staged_operations(self) -> str:
        # TODO: Figure out what to do with this one
        return cmd_svc.get_exec_preview(self.state.get_command_buffer())

    def import_collection_metadata(self, path: Path) -> None:
        ImportCollectionMetadata().call(self.state.get_collection(), path)

    def scan_files_in_path(self,
                           path_string: str,
                           recursive: bool = False) -> None:

        from source.services.scanfilesinpath_svc import ScanFilesInPath
        ScanFilesInPath().call(self.state.get_collection(),
                               path_string,
                               recursive)

    def save_state(self):
        SaveState().call(self.state)

    def load_state(self):
        LoadState().call(self.state)

    def stage_organize_video_files(self,
                                   destination: Optional[str] = None,
                                   format_str: Optional[str] = None,
                                   filter_strings: Optional[list[str]] = None) -> None:

        StageOrganizeVideoFiles().call(self.state.get_collection(),
                                       self.state.get_command_buffer(),
                                       destination,
                                       format_str,
                                       filter_strings)

    def stage_update_api_metadata(self,
                                  api_name: str,
                                  filter_strings: Optional[list[str]] = None) -> None:

        StageUpdateMetadata().call(self.state.get_collection(),
                                   self.state.get_command_buffer(),
                                   api_name,
                                   filter_strings)

    def undo_transaction(self) -> None:
        UndoTransaction().call(self.state.get_batch_history())
