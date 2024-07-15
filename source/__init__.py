# source/__init__.py
import os

# Standard library

# Local imports
from source.constants import *
from source.helper import logger_init

# Third-party packages
from dotenv import load_dotenv


# Initialization
script_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_path, '..', 'config', 'config.env')
load_dotenv(config_path)
logger_init()
