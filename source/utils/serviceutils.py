# source/services/serviceutils.py

# Standard library
from typing import Optional
from types import ModuleType

# Local imports
from source.services.base_service import BaseService
from source.utils import packageutils
from source import services

# Third-party plugins


def get_service_instance(service_name: str, package: ModuleType = services) -> Optional[BaseService]:
    # TODO: Consider raising if None
    plugin_class = packageutils.discover_plugins(package, BaseService, '_svc').get(service_name)
    return plugin_class()
