# source/__init__.py
import os

# Standard library

# Local imports
from source.utils.helper import logger_init
from source.service.configutils import get_user_logs_dir

# Third-party packages
from dotenv import load_dotenv


# Initialization
script_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_path, '..', 'config', 'config.env')
load_dotenv(config_path)
logger_init(get_user_logs_dir())
