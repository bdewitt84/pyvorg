# source/utils/packageutils.py

# Standard library
import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Optional, Type, TypeVar

# Local imports
# n/a

# Third-party plugins
# n/a

T = TypeVar('T')


def discover_subclasses(base_class: type[T], modules) -> dict[str, Type[T]]:
    return {
        class_name: obj
        for class_name, obj
        in inspect.getmembers(modules, inspect.isclass)
        if issubclass(obj, base_class) and obj is not base_class
    }


def discover_modules(package: ModuleType, identifier: str) -> dict[str, ModuleType]:
    modules = pkgutil.iter_modules(package.__path__, package.__name__ + '.')
    return {
        name: importlib.import_module(name)
        for _, name, _
        in modules
        if identifier in name
    }


def discover_plugins(package: ModuleType, base_class: type[T], identifier: str) -> dict[str, type[T]]:
    modules = discover_modules(package, identifier)
    return {
        clsname: cls
        for _, mod
        in modules.items()
        for clsname, cls
        in discover_subclasses(base_class, mod).items()
    }


def get_class_instance(class_name: str, package: ModuleType, base_class: Type[T], identifier: str = '') -> Optional[T]:
    # TODO: Consider raising if None
    class_object = discover_plugins(package, base_class, identifier).get(class_name)
    return class_object()
