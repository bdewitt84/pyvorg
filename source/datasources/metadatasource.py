# ./source/datasources/metadatasource.py

"""

"""

# Standard library
from abc import ABC, abstractmethod

# Local imports

# Third-party packages


class MetadataSource(ABC):
    def __init__(self):
        super(MetadataSource, self).__init__()

    @abstractmethod
    def get_metadata(self):
        raise NotImplementedError("get_metadata() must be implemented in subclass of MetadataSource")

    @abstractmethod
    def get_required_params(self):
        raise NotImplementedError("get_required_params() must be implemented in subclass of MetadataSource")

    @abstractmethod
    def get_optional_params(self):
        raise NotImplementedError("get_optional_params() must be implemented in subclass of MetadataSource")
