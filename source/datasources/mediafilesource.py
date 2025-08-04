# ./source/datasources/mediafilesource.py

"""

"""

# Standard library
from abc import ABC, abstractmethod

# Local imports

# Third-party packages


class MediaFileSource(ABC):
    def __init__(self):
        super(MediaFileSource, self).__init__()

    @abstractmethod
    def get_media_file(self, **kwargs):
        raise NotImplementedError("get_media_file() must be implemented in subclass of MetadataSource")

    @abstractmethod
    def get_optional_params(self) -> list[str]:
        raise NotImplementedError("get_optional_params() must be implemented in subclass of MetadataSource")

    @abstractmethod
    def get_required_params(self) -> list[str]:
        raise NotImplementedError("get_required_params() must be implemented in subclass of MetadataSource")
