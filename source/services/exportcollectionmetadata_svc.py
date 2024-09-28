# ./source/services/exportcollectionmetadata_svc.py

# Standard library
from pathlib import Path

# Local imports
from source.state.col import Collection
from source.utils import \
    collectionutils, \
    serializeutils, \
    fileutils

# Third-party packages
# n/a


class ExportCollectionMetadata:
    def __init__(self):
        pass

    def call(self,
             collection: Collection,
             path: str):
        metadata_dict = collectionutils.get_metadata(collection)
        write_data = serializeutils.dict_to_json(metadata_dict)
        fileutils.file_write(Path(path), write_data)
