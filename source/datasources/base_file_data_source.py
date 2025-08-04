# source/datasources/base_file_data_source.py

"""
    Base class for the plugin interface. Plugins must inherit from this class
    in order to be detected by pluginservice and used by Collection.
"""

# Standard library
from abc import ABC, abstractmethod

# Local imports
# n/a

# Third-party packages
# n/a


class FileDataSource(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_data(self, **kwargs) -> bytes:
        raise NotImplementedError("This function must be implemented in a subclass")

    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    def get_optional_params(self) -> list[str]:
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_required_params(self) -> list[str]:
        raise NotImplementedError("This function must be implemented in a subclass")
