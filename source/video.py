# source/video.py

"""
Video class representing individual videos and their related functions
for use by the Collection class.
"""

# Standard library
import json
import logging
import os

# Local imports
from api import get_omdb_data
from constants import *
from helper import timestamp_generate, hash_sha256

# Third-party packages
import guessit


class Video:
    def __init__(self, path=None):
        self.data = {USER_DATA: {}}
        if path is not None:
            self.update_file_data(path)

    def update_file_data(self, path, skip_hash=False):
        if os.path.exists(path):
            root, file = os.path.split(path)
            timestamp = timestamp_generate()
            if skip_hash is False:
                hash = hash_sha256(path)
            else:
                hash = ''
            file_data = {
                PATH: path,
                ROOT: root,
                FILENAME: file,
                HASH: hash,
                TIMESTAMP: timestamp
            }
            self.data.update({FILE_DATA: file_data})

        else:
            raise FileNotFoundError(f"File {path} not found.")

    def update_guessit(self):
        filename = self.data[FILE_DATA][FILENAME]
        guessit_data = guessit.guessit(filename)
        self.data.update({GUESSIT_DATA: guessit_data})

    def update_omdb(self):
        title = self.get_data('title')
        data = get_omdb_data(title)

        if data:
            self.data.update({OMDB_DATA: data})
            logging.info(f'OMDB videos for {self.data[FILE_DATA][FILENAME]} updated successfully')
        else:
            self.data.update({OMDB_DATA: f'OMDB search for \"{title}\" returned no results.'})

    def set_data(self, key, value):
        self.data.update({
            [USER_DATA]: {
                key: value
            }
        })

    def get_data(self, key, default=None):
        ret = default
        if key in self.data[USER_DATA]:
            ret = self.data[USER_DATA][key]
        else:
            for src in DATA_PREF_ORDER:
                if src in self.data and isinstance(self.data[src], dict):
                    for k in self.data[src].keys():
                        if key.lower() == k.lower():
                            ret = self.data[src][k]
                            break
        return ret

    def update_hash(self):
        self.data[FILE_DATA][HASH] = hash_sha256(self.data[FILE_DATA][PATH])

    def get_hash(self):
        return self.data[FILE_DATA][HASH]

    def get_path(self):
        return self.data[FILE_DATA][PATH]

    def get_filename(self):
        return self.data[FILE_DATA][FILENAME]

    def get_root(self):
        return self.data[FILE_DATA][ROOT]

    def generate_dir_name(self, format='%title (%year)'):
        name = format
        for spec, (key, default) in FORMAT_SPECIFIERS.items():
            data = self.get_data(key, default)
            name = name.replace(spec, str(data))
        return name

    def filter_non_serializable_dict(self, d):
        filtered_dict = {}
        for key, value in d.items():
            if isinstance(value, dict):
                filtered_dict[key] = self.filter_non_serializable_dict(value)
            else:
                try:
                    json.dumps({key: value})
                    filtered_dict[key] = value
                except TypeError:
                    # Object is non-serializable, do not add to dict.
                    print(f'key: {key}, value: {value} is not serializable and was omitted')
                    pass
        return filtered_dict

    def filter_non_serializable_list(self, l):
        pass
