# source/video.py

"""
    Video class representing individual videos and their related functions
    for use by the Collection class.
"""

# Standard library
import json
import os

# Local imports
from constants import *
from helper import timestamp_generate, hash_sha256

# Third-party packages


class Video:
    def __init__(self, path=None):
        self.data = {USER_DATA: {}}
        if path is not None:
            self.update_file_data(path)

    def generate_dir_name(self, format='%title (%year)'):
        name = format
        for spec, (key, default) in FORMAT_SPECIFIERS.items():
            data = self.get_pref_data(key, default)
            name = name.replace(spec, str(data))
        return name

    def get_api_data(self, api_name, key=None):
        data = self.data.get(api_name)
        if key is not None:
            data = data.get(key)
        return data

    def get_filename(self):
        return self.data[FILE_DATA][FILENAME]

    def get_hash(self):
        return self.data[FILE_DATA][HASH]

    def get_path(self):
        return self.data[FILE_DATA][PATH]

    def get_pref_data(self, key, default=None):
        """
        Looks for the key in video data in order of source preference
        designated by DATA_PREF_ORDER, and returns the associated value
        if it is found. Otherwise, the default parameter is returned.

        :param key: The key to search for in the video data
        :param default: Default value to return if the key is not found
        :returns: Value corresponding to key if found, else default
        """

        # TODO: Enhance the preference order routine. Revisit this once
        #       the API management is sorted out

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
                if ret != default:
                    break

        return ret

    def get_root(self):
        return self.data[FILE_DATA][ROOT]

    def get_user_data(self, key):
        return self.data[USER_DATA][key]

    def set_api_data(self, api_name, data):
        self.data.update({api_name: data})

    def set_user_data(self, key, value):
        """
        Used to manually set a key value pair in the video data.
        Will be stored in the USER_DATA entry, which takes priority
        over other sources. e.g., the user can override values returned
        from an API such as an incorrect title.

        :param key: Key name to store in data.[USER_DATA]
        :param value: Value to associate with key
        :return: None
        """
        self.data.update({
            USER_DATA: {
                key: value
            }
        })

    def to_json(self):
        return json.dumps(self.data)

    def update_api_data(self, api):
        data = api.fetch_video_data()
        self.set_api_data(api.get_name(), data)

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

    # def update_guessit(self):
    #     # filename = self.data[FILE_DATA][FILENAME]
    #     filename = self.get_filename()
    #     guessit_data = guessit.guessit(filename)
    #     self.data.update({GUESSIT_DATA: guessit_data})
    #
    # def update_omdb(self):
    #     title = self.get_data('title')
    #     data = get_omdb_data(title)
    #
    #     if data:
    #         self.data.update({OMDB_DATA: data})
    #         logging.info(f'OMDB videos for {self.get_filename()} updated successfully')
    #     else:
    #         self.data.update({OMDB_DATA: f'OMDB search for \"{title}\" returned no results.'})

    def update_hash(self):
        self.data[FILE_DATA][HASH] = hash_sha256(self.data[FILE_DATA][PATH])
