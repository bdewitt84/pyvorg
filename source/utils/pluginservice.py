# source/utils/pluginservice.py

# Standard library
import importlib
import inspect
import pkgutil
from typing import Optional, Type

# Local imports
from source.api.base_api import BaseAPI
import source.api

# Third-party plugins


def get_plugin_instance(api_name: str) -> Optional[BaseAPI]:
    modules = discover_api_modules(package=source.api)
    for mod_name, mod in modules.items():
        for cls_name, cls in discover_api_classes(mod).items():
            if cls_name == api_name:
                return cls()

    # Todo: consider raising here
    return None


def discover_api_modules(package) -> (str, Type):
    """
    Looks for api modules in ./soruce/api/

    :returns: dict of modules ending in '_api.py' in ./source/api/
    """
    modules = pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    api_mods = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in modules
        if '_api' in name
    }
    return api_mods


def discover_api_classes(api_mod) -> (str, Type[BaseAPI]):
    """
    :param api_mod: List of tuples in (str, module) format.
    :return: List of classes that inherit from BaseAPI
    """
    api_classes = {
        class_name: obj
        for class_name, obj
        in inspect.getmembers(api_mod, inspect.isclass)
        if issubclass(obj, BaseAPI) and obj is not BaseAPI
    }
    return api_classes
