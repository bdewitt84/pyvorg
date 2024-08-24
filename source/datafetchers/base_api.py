# source/datafetchers/base_api.py

"""
    Base class for the plugin interface. Plugins must inherit from this class
    in order to be detected by pluginservice and used by Collection.
"""
import json
# Standard library
from abc import ABC, abstractmethod


# class DataFetcher(ABC, metaclass=MetaAPI):
class DataFetcher(ABC):
    def __init__(self, name=None):
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

    @abstractmethod
    def fetch_data(self, **kwargs) -> dict:
        raise NotImplementedError("This function must be implemented in a subclass")

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))

    def get_name(self):
        return self.name

    @abstractmethod
    def get_optional_params(self) -> list[str]:
        raise NotImplementedError("This function must be implemented in a subclass")

    @abstractmethod
    def get_required_params(self) -> list[str]:
        raise NotImplementedError("This function must be implemented in a subclass")

    @classmethod
    def to_dict(cls):
        return {'name': cls.__name__}

    @classmethod
    def to_json(cls):
        json.dumps(cls.to_dict())
