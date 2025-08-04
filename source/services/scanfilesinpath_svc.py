# ./source/services/scanfilesinpath_svc.py

# Standard library
# n/a

# Local imports
from source.state.col import Collection
from source.utils import fileutils, \
                         videoutils, \
                         collectionutils


# Third party packages
# n/a


class ScanFilesInPath:
    def __init__(self):
        # dependency injections go here
        pass

    def call(self,
             collection: Collection,
             path_string: str,
             recursive: bool = False) -> None:

        root, glob_pattern = fileutils.parse_glob_string(path_string)
        file_paths = fileutils.get_files_from_path(root, recursive, glob_pattern)
        videos = videoutils.create_videos_from_file_paths(file_paths)
        collectionutils.add_videos(collection, videos)
