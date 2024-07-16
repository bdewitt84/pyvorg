# source/api/api_interface.py

# Standard library
from abc import ABC, abstractmethod


class APIInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_video_data(self, **kwargs):
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_name(self):
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_optional_params(self):
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_required_params(self):
        raise NotImplementedError("This function must be implemented in a subclass")
