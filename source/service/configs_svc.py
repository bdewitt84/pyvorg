# source/service/configs_svc.py

# Standard library
import os
from pathlib import Path
import platform

# Local imports
from constants import APP_NAME,\
                      ENV_DEST_PATH

# Third-party packages
# n\a


def get_default_dst_tree():
    return os.getenv(ENV_DEST_PATH)


def get_default_format_str():
    return os.getenv('DEFAULT_FORMAT_STRING')


def get_user_cache_dir():
    system = platform.system()

    if system == 'Windows':
        cache_dir = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / 'Cache'
    else:
        # TODO: Implement default case
        cache_dir = Path()

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_user_config_dir():
    system = platform.system()

    if system == 'Windows':
        config_dir = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / 'Config'
    else:
        # TODO: Implement default case
        config_dir = Path()

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_user_export_dir():
    system = platform.system()

    if system == 'Windows':
        export_dir = Path.home() / 'Documents' / APP_NAME / 'Export'
    else:
        # TODO: Implement default case
        export_dir = Path()

    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def get_user_profile_dir():
    system = platform.system()

    if system == 'Windows':
        profile_dir = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / 'Profiles'
    else:
        # TODO Implement default case
        profile_dir = Path()

    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


def get_user_logs_dir():
    system = platform.system()

    if system == 'Windows':
        logs_dir = Path(os.getenv('LOCALAPPDATA')) / APP_NAME / 'Logs'
    else:
        # TODO: Implement default case
        logs_dir = Path()

    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
