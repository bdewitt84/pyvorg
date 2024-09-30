# source/services/pluginutils.py

# Standard library
import importlib
import inspect
import pkgutil
from typing import Optional, Type
from types import ModuleType

# Local imports
from source.datasources.base_metadata_source import MetadataSource
from source.utils import packageutils

# Third-party plugins


def discover_api_classes(api_mod) -> (str, Type[MetadataSource]):
    return {
        class_name: obj
        for class_name, obj
        in inspect.getmembers(api_mod, inspect.isclass)
        if issubclass(obj, MetadataSource) and obj is not MetadataSource
    }


def discover_api_modules(package: ModuleType) -> (str, Type):
    modules = pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    return {
        name: importlib.import_module(name)
        for _, name, _
        in modules
        if '_plugin' in name
    }


def discover_plugins(package: ModuleType) -> dict[str, type[MetadataSource]]:
    modules = discover_api_modules(package)
    return {
        clsname: cls
        for _, mod
        in modules.items()
        for clsname, cls
        in discover_api_classes(mod).items()
    }


def get_plugin_instance(api_name: str, package: ModuleType) -> Optional[MetadataSource]:
    # TODO: Consider raising if None
    plugin_class = packageutils.discover_plugins(package, MetadataSource, '_plugin').get(api_name)
    return plugin_class()


def get_required_params(api: MetadataSource) -> list[str]:
    return api.get_required_params()
