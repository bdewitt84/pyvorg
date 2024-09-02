# source/service/serialize_svc.py

# Standard library
import pickle
import json

# Local imports

# Third-party packages


def dict_to_json(input_dict: dict):
    return json.dumps(dict)


def dict_to_xml(input_dict: dict):
    pass

def obj_to_pickle(input_obj: type(object)) -> bytes:
    return pickle.dumps(input_obj)


def pickle_to_object(pickle_bytes: bytes) -> type(object):
    return pickle.loads(pickle_bytes)
