# source/video.py

"""
    Video class representing individual videos and their related functions
    for use by the Collection class.
"""

# Standard library
import logging
from pathlib import Path
from typing import Any, Optional

# Local imports
from source.constants import *
from source.service.file_svc import hash_sha256
from source.utils.helper import get_preferred_sources, timestamp_generate

# Third-party packages


# TODO: Refactor to Media


class Video:
    def __init__(self, path: Path = None):
        self.data = {USER_DATA: {}}
        if path is not None:
            self.update_file_data(path)

    # TODO: This belongs in services
    def append_available_sources(self, sources: list) -> None:
        for source in self.get_source_names():
            if source not in sources:
                sources.append(source)

    def get_filename(self) -> str:
        return self.data[FILE_DATA][FILENAME]

    def get_hash(self) -> str:
        return self.data[FILE_DATA][HASH]

    def get_path(self) -> Path:
        return Path(self.data[FILE_DATA][PATH]).resolve()

    def get_pref_data(self, key: str, default: Optional[str] = None, fill: bool = True) -> Any:
        ordered_sources = get_preferred_sources()

        if fill is True:
            self.append_available_sources(ordered_sources)

        for source in ordered_sources:
            for source_key in self.get_source_keys(source):
                if key.lower() == source_key.lower():
                    return self.get_source_data(source, source_key)
        return default

    def get_root(self) -> Path:
        return Path(self.data[FILE_DATA][ROOT])

    def get_source_data(self, api_name: str, key: Optional[str] = None) -> Any:
        data = self.data.get(api_name)
        if key is not None:
            data = data.get(key)
        return data

    def get_source_keys(self, source_name: Optional[str] = None) -> list:
        if source_name:
            if self.data.get(source_name):
                return list(self.data.get(source_name).keys())
            else:
                return []
        else:
            return [key for source in self.data.values() for key in source.keys()]

    def get_source_names(self) -> list[str]:
        return list(self.data.keys())

    def get_user_data(self, key: str) -> str:
        return self.data[USER_DATA][key]

    def set_hash(self, sha256) -> None:
        self.data[FILE_DATA][HASH] = sha256

    def set_source_data(self, api_name: str, data: dict) -> None:
        self.data.update({api_name: data})

    def set_user_data(self, key: str, value):
        # TODO: Should this simply be part of set_source_data?
        #       consider renaming to override?
        self.data.update(
            {
                USER_DATA: {
                    key: value
                }
            }
        )

    def to_dict(self) -> dict:
        return self.data

    def update_file_data(self, path: Path, skip_hash: bool = False) -> None:
        # TODO: Add member for 'media_type'
        if not path.exists() or not path.is_file():
            msg = f"Cannot update info for '{path}': file not found."
            logging.error(msg)
            raise FileNotFoundError(msg)

        path = path.resolve()

        file_data = {
            PATH: str(path),
            ROOT: str(path.parent),
            FILENAME: path.name,
            HASH: '',
            TIMESTAMP: timestamp_generate()
        }

        if skip_hash is False:
            file_data.update({HASH: hash_sha256(path)})

        self.data.update({FILE_DATA: file_data})

    def update_hash(self) -> None:
        # TODO: Should this be Videos responsibility?
        self.set_hash(hash_sha256(self.get_path()))
