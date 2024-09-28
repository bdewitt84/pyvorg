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


class ImportCollectionMetadata:
    def __init__(self):
        pass

    def call(self,
             collection: Collection,
             path: Path):
        metadata = fileutils.file_read(path)
        collectionutils.validate_metadata(metadata)
        collectionutils.import_metadata(collection, metadata)