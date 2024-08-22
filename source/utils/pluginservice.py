# source/utils/pluginservice.py

# Standard library
import importlib
import inspect
import pkgutil
from typing import Optional, Typefrom types import ModuleType

# Local imports
from source.api.base_api import BaseAPI
import source.api

# Third-party plugins


def discover_api_classes(api_mod) -> (str, Type[BaseAPI]):
    return {
        class_name: obj
        for class_name, obj
        in inspect.getmembers(api_mod, inspect.isclass)
        if issubclass(obj, BaseAPI) and obj is not BaseAPI
    }


def discover_api_modules(package: ModuleType) -> (str, Type):
    modules = pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    return {
        name: importlib.import_module(name)
        for _, name, _
        in modules
        if '_api' in name
    }


def discover_plugins(package: ModuleType):
    modules = discover_api_modules(package)
    return {
        clsname: cls
        for _, mod
        in modules.items()
        for clsname, cls
        in discover_api_classes(mod).items()
    }


def get_plugin_instance(api_name: str) -> Optional[BaseAPI]:
    # TODO: Consider raising if None
    # TODO: need to request or pass the plugin package instead
    plugin_class = discover_plugins(source.api).get(api_name)
    return plugin_class()


def get_required_params(api: BaseAPI):
    return api.get_required_params()
