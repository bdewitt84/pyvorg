# source/api/base_api.py

# Standard library
from abc import ABC, abstractmethod


# class BaseAPI(ABC, metaclass=MetaAPI):
class BaseAPI(ABC):
    def __init__(self, name=None):
        self.name = name

    @abstractmethod
    def fetch_video_data(self, **kwargs):
        raise NotImplementedError("This function must be implemented in a subclass")

    def get_name(self):
        return self.name

    @abstractmethod
    def get_optional_params(self):
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_required_params(self):
        raise NotImplementedError("This function must be implemented in a subclass")
