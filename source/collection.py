# source.collection.py

"""
    Collection class handles the main functionality of the package, including
    scanning for files, updating the metadata from online sources, and organizing
    the video files into a predefined file structure.
"""

# Standard library
import json
import os

# Local imports
from source.combuffer import CommandBuffer
from source.constants import *
from source.exceptions import ValidationError
from source.video import Video


class Collection:
    def __init__(self, path=None):
        self.videos = {}
        self.cb = CommandBuffer()
        if path:
            self.load_metadata(path)

    def load_metadata(self, path="./metadata.json"):
        with open(path, 'r') as file:
            serializable = json.load(file)

        for entry in serializable:
            video = Video()
            video.data = serializable.get(entry)
            self.videos.update({entry: video})

    def save_metadata(self, path="./metadata.json"):
        serializable = {}

        for video in self.videos.values():
            serializable.update({video.get_hash(): video.data})

        with open(path, 'w') as file:
            json.dump(serializable, file, indent=4, skipkeys=True)

    def add_video(self, path):
        video = Video()
        video.update_file_data(path)
        self.videos.update({video.get_hash(): video})

    def get_video(self, hash):
        video = None
        if hash in self.videos:
            video = self.videos.get(hash)
        return video

    def update_guessit(self):
        for video in self.videos.values():
            video.update_guessit()

    def update_omdb(self):
        for video in self.videos.values():
            video.update_omdb()

    def scan_directory(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(VIDEO_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    self.add_video(file_path)

    def organize_files(self, dest_dir):
        cb = CommandBuffer()

        for video in self.videos.values():
            vid_dir = video.generate_dir_name()
            dest = os.path.join(dest_dir, vid_dir)

            # TODO: Probably add member function to do this so we
            #       don't have to expose the Commands to the user
            # cb.add_command(CreateVideoDirectory(video, dest))
            #
            # cb.add_command(MoveVideo(video, dest))

            cb.add_create_video_dir(video, dest)
            cb.add_move_video(video, dest)

        cb.preview_buffer()
        user_input = self.user_prompt('(a) Abort\n(c) Continue\n', ['a', 'c'])
        while user_input != 'a':
            try:
                if user_input == 'c':
                    cb.validate_exec_buffer()
                    # cb.execute_command_buffer()

                if user_input == 'u':
                    cb.validate_undo_buffer()
                    # cb.execute_undo_buffer()

            except ValidationError as e:
                user_input = self.user_prompt(
                    f'Validation error: {e}\n(a) Abort\n(c) Continue\n(u) Undo Changes\n',
                    ['a', 'c', 'u']
                )

            # except Exception as e:
            #     user_input = self.user_prompt(
            #         f'Unexpected exception: {e}\n{e.with_traceback()}(a) Abort\n(c) Continue\n(u) Undo Changes\n',
            #         ['a', 'c', 'u']
            #     )

        self.save_metadata()

    def user_prompt(self, prompt, valid_input):
        valid = False
        while valid is False:
            inp = input(prompt).lower()
            if inp in valid_input:
                valid = True
            else:
                print(f'The valid choices are {valid_input}')
        return inp

    def filter_non_serializable(self):
        for video in self.videos.values():
            video.data = video.filter_non_serializable_dict(video.data)