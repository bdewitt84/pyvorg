# tests/test_collection.py
import json
# Standard library
import os.path
import tempfile
import unittest

# Local imports
from source.collection.collection import Collection
from source.collection.video import Video


class UnserializableObject:
    """Used by 'test_save_metadate_unserializable'"""

    def __init__(self):
        value = None


class TestMetadataSave(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = self.temp_dir.name
        self.save_file_path = os.path.join(self.temp_dir_path, 'test_save.json')

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_metadata_save_valid(self):
        c = Collection()
        test_vid_1 = Video()
        test_vid_2 = Video()
        test_vid_1.data.update(
            {
                "user_data": {},
                "file_data": {
                    "path": "C:/videos\\Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
                    "root": "C:/videos",
                    "filename": "Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
                    "hash": "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
                    "timestamp": "2024-07-05 22:18:38"
                },
                "guessit": {
                    "title": "Extraction 2",
                    "year": 2023,
                    "screen_size": "1080p",
                    "audio_codec": "Dolby Digital",
                    "audio_channels": "5.1",
                    "video_codec": "H.264",
                    "container": "mkv",
                    "mimetype": "video/x-matroska",
                    "type": "movie"
                }
            }
        )
        test_vid_2.data.update(
            {
                "user_data": {},
                "file_data": {
                    "path": "C:/videos\\02. Manhattan Connection [480i] [Dual Audio] [AC-3] [English Subtitles] ["
                            "VobSub].mp4",
                    "root": "C:/videos\\Mad-Bull-34-480i",
                    "filename": "02. Manhattan Connection [480i] [Dual Audio] [AC-3] [English Subtitles] [VobSub].mp4",
                    "hash": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
                    "timestamp": "2024-07-05 22:18:38"
                },
                "guessit": {
                    "episode": 2,
                    "title": "Manhattan Connection",
                    "screen_size": "480i",
                    "other": "Dual Audio",
                    "audio_codec": "Dolby Digital",
                    "release_group": "VobSub",
                    "container": "mp4",
                    "mimetype": "video/mp4",
                    "type": "episode"
                }
            }
        )
        c.videos.update({"5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": test_vid_1})
        c.videos.update({"7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451": test_vid_2})

        # Indentation looks bad, but must be maintained to pass test
        expected_json = """{
    "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": {
        "user_data": {},
        "file_data": {
            "path": "C:/videos\\\\Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
            "root": "C:/videos",
            "filename": "Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
            "hash": "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
            "timestamp": "2024-07-05 22:18:38"
        },
        "guessit": {
            "title": "Extraction 2",
            "year": 2023,
            "screen_size": "1080p",
            "audio_codec": "Dolby Digital",
            "audio_channels": "5.1",
            "video_codec": "H.264",
            "container": "mkv",
            "mimetype": "video/x-matroska",
            "type": "movie"
        }
    },
    "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451": {
        "user_data": {},
        "file_data": {
            "path": "C:/videos\\\\02. Manhattan Connection [480i] [Dual Audio] [AC-3] [English Subtitles] [VobSub].mp4",
            "root": "C:/videos\\\\Mad-Bull-34-480i",
            "filename": "02. Manhattan Connection [480i] [Dual Audio] [AC-3] [English Subtitles] [VobSub].mp4",
            "hash": "7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451",
            "timestamp": "2024-07-05 22:18:38"
        },
        "guessit": {
            "episode": 2,
            "title": "Manhattan Connection",
            "screen_size": "480i",
            "other": "Dual Audio",
            "audio_codec": "Dolby Digital",
            "release_group": "VobSub",
            "container": "mp4",
            "mimetype": "video/mp4",
            "type": "episode"
        }
    }
}"""
        c.metadata_save(self.save_file_path)
        with open(self.save_file_path, 'r') as file:
            actual_result = file.read()
            self.assertEqual(expected_json, actual_result)

    def test_metadata_save_unserializable(self):
        c = Collection()
        test_video = Video()
        test_video.data.update(
            {"Unserializable": UnserializableObject()}
        )
        c.videos.update({"5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": test_video})

        # Indentation looks bad, but must be maintained to pass test
        expected = """{
    "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": {
        "user_data": {},
        "Unserializable": "Object 'UnserializableObject' is not serializable"
    }
}"""
        c.metadata_save(self.save_file_path)
        with open(self.save_file_path, 'r') as actual:
            self.assertEqual(expected, actual.read())

    def test_metadata_save_file_exists(self):
        c = Collection()
        test_vid = Video()
        c.videos.update({"5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": test_vid})
        with open(self.save_file_path, 'w') as file:
            file.write('test data')

        with self.assertRaises(FileExistsError):
            c.metadata_save(self.save_file_path)


class TestMetadataLoad(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = self.temp_dir.name
        self.c = Collection()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_metadata_load_valid(self):
        data = """
{
    "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": {
        "user_data": {},
        "file_data": {
            "path": "C:/Videos\\\\Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
            "root": "C:/Videos",
            "filename": "Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
            "hash": "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
            "timestamp": "2024-07-05 22:18:38"
        },
        "guessit": {
            "title": "Extraction 2",
            "year": 2023,
            "type": "movie"
        }
    }
}"""
        valid_json_path = os.path.join(self.temp_dir_path, "temp.file")
        with open(valid_json_path, 'w') as file:
            file.write(data)

        self.c.metadata_load(valid_json_path)
        expected_video_data = {
            "user_data": {},
            "file_data": {
                "path": "C:/Videos\\Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
                "root": "C:/Videos",
                "filename": "Extraction.2.2023.1080p.NF.WEBRip.1400MB.DD5.1.x264-GalaxyRG.mkv",
                "hash": "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
                "timestamp": "2024-07-05 22:18:38"
            },
            "guessit": {
                "title": "Extraction 2",
                "year": 2023,
                "type": "movie"
            }
        }
        actual_video_data = self.c.videos.get("5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9").data
        self.assertEqual(expected_video_data, actual_video_data)

    def test_metadata_load_invalid(self):
        data = """
        {
            "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9": {
                "user_data": {}
            }
        """
        valid_json_path = os.path.join(self.temp_dir_path, "temp.file")
        with open(valid_json_path, 'w') as file:
            file.write(data)

        with self.assertRaises(json.JSONDecodeError):
            self.c.metadata_load(valid_json_path)

    def test_metadata_load_does_not_exist(self):
        valid_json_path = os.path.join(self.temp_dir_path, "temp.file")
        with self.assertRaises(FileNotFoundError):
            self.c.metadata_load(valid_json_path)
