# source/__init__.py

# Standard library

# Local
from source.helper import logger_init

# Third-party packages
from dotenv import load_dotenv


# Initialization
load_dotenv('./config.env')
logger_init()
