# source/constants.py

"""
    Constants used across all packages, mostly to standardize JSON entries.
    Also included are a list of valid video extensions and a JSON schema
    used for validating metadata.
"""

# Environment variable constants
ENV_FILE_PATH = './config.env'
ENV_OMDB_KEY = 'OMDB_KEY'

# String constants
FILE_DATA = 'file_data'
OMDB_DATA = 'omdb_data'
OMDB_TITLE = 'Title'
OMDB_YEAR = 'Year'
GUESSIT_DATA = 'guessit'
GUESSIT_TITLE = 'title'
GUESSIT_YEAR = 'year'
USER_DATA = 'user_data'
USER_TITLE = 'title'
USER_YEAR = 'year'
PATH = 'path'
ROOT = 'root'
FILENAME = 'filename'
HASH = 'hash'
TIMESTAMP = 'timestamp'
LOCAL_TRAILER = 'local_trailer'

# TODO: move this to config.env
DATA_PREF_ORDER = [USER_DATA, OMDB_DATA, GUESSIT_DATA]

FORMAT_SPECIFIERS = {
    '%title': ('title', 'unknown title'),
    '%year': ('year', 'n.d.')
}

VIDEO_EXTENSIONS = (            # TODO: Should this be loaded from an external file? Consider keeping this as a default
        '.3g2', '.3gp', '.amv', '.asf', '.avi', '.divx', '.drc', '.f4v', '.flv', '.gvi',
        '.gxf', '.ismv', '.iso', '.m1v', '.m2v', '.m2ts', '.m4v', '.mkv', '.mov', '.mp2',
        '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg2', '.mpeg4', '.mpg', '.mpv2',
        '.mts', '.mxf', '.mxg', '.nsv', '.ogm', '.ogv', '.qt', '.rm', '.rmvb', '.roq',
        '.scm', '.smv', '.swf', '.ts', '.vob', '.webm', '.wmv', '.yuv'
    )
