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

METADATA_SCHEMA = {
        "type": "object",
        "patternProperties": {
            "^[0-9a-fA-F]{64}$": {
                "type": "object",
                "properties": {
                    "file_data": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"},
                            "root": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        },
                        "required": ["filename", "root", "timestamp"]
                    },
                    "omdb_data": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"}
                        },
                        "required": ["title"]
                    }
                },
                "required": ["file_data"]
            }
        },
        "additionalProperties": False
    }