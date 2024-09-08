# source/service/collection_svc.py

# Standard library

# Local imports
from source.state.col import Collection
from source.filter import Filter

# Third-party packages

# TODO: Implement support for other media types
#       Add methods:
#           add_media()


def add_videos(collection: Collection, videos) -> None:
    for video in videos:
        collection.add_video_instance(video)


def apply_filter(videos, filter_string) -> list:
    f = Filter.from_string(filter_string)
    return [video for video in videos if f.matches(video.get_pref_data(f.key))]


def get_metadata(collection: Collection) -> dict:
    return {
        video_id: video.to_dict()
        for video_id, video
        in zip(collection.get_video_ids(), collection.get_videos())
    }


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
