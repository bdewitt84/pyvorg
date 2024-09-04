# source/service/serialize_svc.py

# Standard library
import pickle
import json

# Local imports

# Third-party packages


def dict_to_json(input_dict: dict):
    return json.dumps(input_dict,
                      indent=4,
                      skipkeys=True)


def dict_to_xml(input_dict: dict):
    raise NotImplementedError("dict_to_xml has not been implemented")


def obj_to_pickle(input_obj: type(object)) -> bytes:
    return pickle.dumps(input_obj)


def pickle_to_object(pickle_bytes: bytes) -> type(object):
    try:
        obj = pickle.loads(pickle_bytes)
        if isinstance(obj, object):
            return obj
    except EOFError:
        return None
