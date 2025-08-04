# .source/services/base_service.py

# Standard library
from abc import ABC, abstractmethod

# Local imports
# n/a

# Third-party packages
# n/a


class BaseService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError("method 'call()' must be implemented in subclasses of BaseService")
