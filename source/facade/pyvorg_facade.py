# ./source/facade/pyvorg_facade.py

"""
    Acts as entry point for user interface.
    Should only interact with the services layer.
"""

# Standard library
from pathlib import Path
from typing import Optional

# Local imports
from source.state.application_state import PickleJar
from source.state.col import Collection
from source.commands.cmdbuffer import CommandBuffer
from source.utils import serializeutils as serial_svc
from source.utils import fileutils as file_svc
from source.utils import configutils as cfg_svc
from source.utils import cmdutils as cmd_svc, collectionutils as col_svc


# Third-party packages
# n\a


# TODO: We'll refactor MediaFile to be any arbitrary media file.
#       Maybe use MediaFile as a base, with MediaFile and Subtitle as subclasses
#       when we scan we can add media files to the collection based on file extension
#       consider simply adding 'type:value' key value pair to file info
#       then we can easily apply filters


class Facade:
    def __init__(self, collection: Collection, command_buffer: CommandBuffer):
        self.collection = collection
        self.command_buffer = command_buffer
        self.command_buffer_history: list[command_buffer] = []

    def clear_staged_operations(self) -> None:
        cmd_svc.clear_exec_buffer(self.command_buffer)

    def commit_staged_operations(self) -> None:
        cmd_svc.execute_cmd_buffer(self.command_buffer)
        self.command_buffer_history.append(self.command_buffer)
        self.command_buffer = CommandBuffer()

    def export_collection_metadata(self, path: str) -> None:
        metadata_dict = col_svc.get_metadata(self.collection)
        write_data = serial_svc.dict_to_json(metadata_dict)
        file_svc.file_write(Path(path), write_data)

    def get_preview_of_staged_operations(self) -> str:
        return cmd_svc.get_exec_preview(self.command_buffer)

    def import_collection_metadata(self, path: Path) -> None:
        metadata = file_svc.file_read(path)
        col_svc.validate_metadata(metadata)
        col_svc.import_metadata(self.collection, metadata)

    def scan_files_in_path(self,
                           path_string: str,
                           recursive: bool = False) -> None:
        from source.services.scanfilesinpath_svc import ScanFilesInPath
        ScanFilesInPath().call(self.collection, path_string, recursive)

    def save_state(self):
        jar = PickleJar(self.collection,
                        self.command_buffer,
                        self.command_buffer_history)
        jar_path = cfg_svc.get_default_state_path()
        serialized_state = serial_svc.obj_to_pickle(jar)
        file_svc.file_write_bytes(jar_path, serialized_state, overwrite=True)

    def load_state(self):
        jar_path = cfg_svc.get_default_state_path()
        serialized_state = file_svc.file_read_bytes(jar_path)
        state: PickleJar = serial_svc.pickle_to_object(serialized_state) or PickleJar()
        # TODO: Verify and validate that loaded objects are the correct classes
        self.collection = state.collection
        self.command_buffer = state.command_buffer
        self.command_buffer_history = state.batch_history

    def stage_organize_video_files(self,
                                   destination: Optional[str] = None,
                                   format_str: Optional[str] = None,
                                   filter_strings: Optional[list[str]] = None) -> None:

        from source.services.stageorganizevideofiles_svc import StageOrganizeVideoFiles
        StageOrganizeVideoFiles().call(self.collection,
                                       self.command_buffer,
                                       destination,
                                       format_str,
                                       filter_strings)

    def stage_update_api_metadata(self,
                                  api_name: str,
                                  filter_strings: Optional[list[str]] = None) -> None:
        from source.services.stageupdatemetadata_svc import StageUpdateMetadata
        StageUpdateMetadata().call(self.collection,
                                   self.command_buffer,
                                   api_name,
                                   filter_strings)

    def undo_transaction(self) -> None:
        from source.services.undotransaction_svc import UndoTransaction
        UndoTransaction().call(self.command_buffer_history)
