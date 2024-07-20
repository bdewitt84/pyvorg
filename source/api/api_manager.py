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
import pkgutil

# Local imports
from source.api.base_api import BaseAPI
import source.api

# Third-party packages


class APIManager:
    def __init__(self):
        self.apis = {}

    def discover_api_modules(self):
        """
        Looks for api modules in ./soruce/api/

        :returns: list of modules ending in '_api.py' in ./source/api/
        """
        pkgs = pkgutil.iter_modules(source.api.__path__, source.api.__name__ + '.')
        api_mods = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgs
            if '_api' in name
        }
        return api_mods

    def discover_api_classes(self, api_mods):
        """
        Takes a list of modules and finds within them any classes that inherit from BaseAPI

        :param api_mods: List of tuples in (str, module) format.
        :return: List of classes that inherit from BaseAPI
        """
        api_classes = {}
        for mod_name, mod in api_mods:
            for class_name, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, BaseAPI):
                    api_classes.update({class_name: obj})
        return api_classes

    def register_apis(self, api_classes):
        """
        Takes a list of classes which inherit from BaseAPI, instantiates them,
        then adds the instances to the dict self.api of {name: api} pairs.

        :param api_classes: List of tuples in (str, class) format
        :return: None
        """
        for name, api_class in api_classes.items():
            self.apis.update({name: api_class()})

    def init_plugins(self):
        """
        Discovers and instantiates all api plugins found in ./source/api/.
        To be run before accessing any api plugin functions.

        :return: None
        """
        mods = self.discover_api_modules()
        classes = self.discover_api_classes(mods)
        self.register_apis(classes)

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
