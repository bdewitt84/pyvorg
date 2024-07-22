# source/api/api_manager.py

"""
    APIManager class handles detection of plugins in the plugin folder.
    init_api() will look for any modules in './source/api/' ending with
    '_api.py'. Any classes within those modules inheriting from BaseAPI
    will be registered as an api plugin.
"""

# Standard Library
import importlib
import inspect
import logging
import pkgutil

# Local imports
from source.api.base_api import BaseAPI
import source.api

# Third-party packages


class APIManager:
    def __init__(self):
        self.apis = {}

    def discover_api_modules(self, pkg):
        """
        Looks for api modules in ./soruce/api/

        :returns: dict of modules ending in '_api.py' in ./source/api/
        """
        modules = pkgutil.iter_modules(pkg.__path__, pkg.__name__ + '.')
        print(modules)
        api_mods = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in modules
            if '_api' in name
        }
        return api_mods

    def discover_api_classes(self, api_mod):
        """
        :param api_mods: List of tuples in (str, module) format.
        :return: List of classes that inherit from BaseAPI
        """
        api_classes = {}
        for class_name, obj in inspect.getmembers(api_mod, inspect.isclass):
            if issubclass(obj, BaseAPI):
                api_classes.update({class_name: obj})
        return api_classes


    def register_api(self, name, api_class):
        """
        Takes a name and a class which inherrits from BaseAPI, then
        creates an instance of that class and registers it in self.apis{name:instance}

        :param name: Name of api to store in registry. Used for retrieval.
        :param api_class: Class to register
        :return: None
        """
        if issubclass(api_class, BaseAPI):
            self.apis.update({name: api_class()})
        else:
            msg = f"Argument  '{api_class}'  must inherit from BaseAPI."
            logging.error(msg)
            raise TypeError(msg)

    def init_plugins(self):
        """
        Discovers and instantiates all api plugins found in ./source/api/.
        To be run before accessing any api plugin functions.

        :return: None
        """
        src_pkg = source.api
        api_mods = self.discover_api_modules(src_pkg)
        for mod_name, mod in api_mods.items():
            for cls_name, cls in self.discover_api_classes(mod).items():
                self.register_api(cls_name, cls)

    def get_api(self, api_name):
        """
        Gets the instance of the api plugin associated with key 'api_name'

        :param api_name: name of api to get
        :return: instance of api plugin class inheriting from BaseAPI
        """
        if api_name in self.apis.keys():
            return self.apis.get(api_name)
        else:
            raise ValueError(f"'{api_name}' is not registered in the api manager.")

    def get_api_list(self):
        """
        Returns list of instances of each plugin initialized by APIManager

        :return: list
        """
        return [api for api in self.apis.values()]

    def get_api_names(self):
        """
        Returns the list of names of each plugin initialized by APIManager

        :return: list of api plugin names
        """
        return [name for name in self.apis.keys()]
