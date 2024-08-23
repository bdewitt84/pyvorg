# source/service/configservice.py

# Standard library
import os

# Local imports

# Third-party packages
# n\a


def get_default_format_str():
    return os.getenv('DEFAULT_FORMAT_STRING')
