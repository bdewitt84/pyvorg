# source/api/api_interface.py

# Standard library
from abc import ABC, abstractmethod


class APIInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_video_data(self, title):
        raise NotImplementedError("This function must be called from a subclass of APIInterface, not APIInterface "
                                  "itself.")
