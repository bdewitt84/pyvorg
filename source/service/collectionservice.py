# source/service/collectionservice.py

# Standard library
from typing import Optional

# Local imports
from source.collection.col import Collection
from source.filter import Filter

# Third-party packages


def add_videos(collection, videos) -> None:
    for video in videos:
        collection.add_video_instance(video)


def apply_filter(videos, filter_string) -> list:
    f = Filter.from_string(filter_string)
    return [video for video in videos if f.matches(video.get_pref_data(f.key))]


def get_metadata(collection: Collection, filter_strings) -> str:
    return collection.to_json(filter_strings)


def get_filtered_videos(collection: Collection, filter_strings: list[str]) -> list:
    ret = collection.get_videos()
    if filter_strings:
        for string in filter_strings:
            ret = apply_filter(ret, string)
    return ret


def import_metadata(collection, metadata, overwrite=True):
    # TODO: Consider using or writing Collection methods
    #       so we don't have to directly access video member
    if overwrite:
        collection.videos = collection.videos | metadata
    else:
        collection.videos = metadata | collection.videos


def validate_metadata(metadata) -> None:
    # Todo: implement
    # Should we raise or return bool?
    return None
