import json
from json.decoder import JSONDecodeError
import os
import time
import unittest
from unittest.mock import MagicMock, Mock, patch
import tempfile
import jsonschema
from main import hash_sha256
from main import add_video
from main import generate_timestamp
from main import validate_timestamp
from main import scan_directory
from main import guess_title
from main import get_omdb_data
from main import update_omdb_data
from main import save_metadata
from main import load_metadata
from main import validate_metadata

from constants import *


class HashSHA256(unittest.TestCase):

    def test_hash_sha256_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'Test data')
            temp_file.close()

            expected_hash = 'e27c8214be8b7cf5bccc7c08247e3cb0c1514a48ee1f63197fe4ef3ef51d7e6f'
            computed_hash = hash_sha256(temp_file.name)

            os.remove(temp_file.name)

            self.assertEqual(computed_hash, expected_hash)

    def test_hash_sha256_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            hash_sha256('bogus_file_name')


class TestAddVideo(unittest.TestCase):

    def test_add_video_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'Test data')
            temp_file.close()

            collection = {}
            path = temp_file.name

            expected_hash = hash_sha256(path)
            # expected_timestamp = generate_timestamp()

            add_video(collection, path)

            self.assertIn(expected_hash, collection)
            self.assertEqual(collection[expected_hash][FILE_DATA][FILENAME], os.path.basename(path))
            self.assertEqual(collection[expected_hash][FILE_DATA][ROOT], os.path.dirname(path))
            self.assertTrue(validate_timestamp(collection[expected_hash][FILE_DATA][TIMESTAMP]))
            # self.assertEqual(collection[expected_hash][FILE_DATA][TIMESTAMP], expected_timestamp)


class TestScanDirectory(unittest.TestCase):

    def setUp(self) -> None:
        self.collection = {}
        self.temp_dir = tempfile.TemporaryDirectory()

        test_files = ['video1.mp4', 'video2.mkv', 'notavideo.txt']
        for filename in test_files:
            path = os.path.join(self.temp_dir.name, filename)
            with open(path, 'w') as file:
                file.write(filename)  # We use unique data to produce unique hashes

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_scan_directory_valid(self):
        mock_add_video = MagicMock()

        with unittest.mock.patch('main.add_video', mock_add_video):
            scan_directory(self.collection, self.temp_dir.name)

        self.assertEqual(mock_add_video.call_count, 2)


class TestGuessTitle(unittest.TestCase):

    def test_guess_title(self):
        filename = 'Three.Outlaw.Samurai.1964.JAPANESE.1080p.BluRay.H264.AAC-VXT.mp4'
        mock_video = {
            FILE_DATA: {
                FILENAME: filename
            }
        }

        expected_guess = 'Three Outlaw Samurai'
        guess = guess_title(mock_video)
        self.assertEqual(expected_guess, guess)


class TestGetOMDBData(unittest.TestCase):

    @patch('requests.get')
    def test_get_omdb_data_success(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Title": "Three Outlaw Samurai",
            "Response": "True"
        }

        mock_requests_get.return_value = mock_response

        result = get_omdb_data('Three Outlaw Samurai')

        self.assertEqual(result, {"Title": "Three Outlaw Samurai", "Response": "True"})

    @patch('requests.get')
    def test_get_omdb_data_bad_title(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Movie not found!"
        }

        mock_requests_get.return_value = mock_response

        result = get_omdb_data('bogusmovietitle')

        self.assertIsNone(result)


class TestUpdateOMDBData(unittest.TestCase):

    @patch('main.get_omdb_data')
    @patch('main.guess_title')
    def test_update_omdb_data_valid(self, mock_guess_title, mock_get_omdb_data):

        mock_guess_title.return_value = 'Movie Title'

        mock_get_omdb_data.return_value = {
            "Title": "Movie Title",
            "Response": "True"
        }

        expected_video = {
            FILE_DATA: {
                FILENAME: "Mock_Video.mp4"
            },
            OMDB_DATA: {
                "Title": "Movie Title",
                "Response": "True"
            }
        }

        mock_video = {
            FILE_DATA: {
                FILENAME: "Mock_Video.mp4"
            }
        }

        update_omdb_data(mock_video)

        self.assertEqual(expected_video, mock_video)


class TestSaveMetadata(unittest.TestCase):

    def test_save_metadata_valid(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = temp_dir.name
        collection = {'data': 'test'}
        expected_file_path = os.path.join(path, 'metadata.json')

        save_metadata(collection, path)

        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path, 'r') as temp_file:
            file_content = json.load(temp_file)
            self.assertEqual(collection, file_content)

        temp_dir.cleanup()


class TestLoadMetadata(unittest.TestCase):

    def test_load_metadata_valid(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, 'metadata.json')
        collection = {"data": "test"}

        with open(path, 'w') as temp_file:
            json.dump(collection, temp_file, indent=4)

        result = load_metadata(path)

        self.assertEqual(collection, result)

        temp_dir.cleanup()

    def test_load_metadata_file_not_found(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, 'metadata.json')

        with self.assertRaises(FileNotFoundError):
            load_metadata(path)

        temp_dir.cleanup()

    def test_load_metadata_invalid_json(self):

        with tempfile.NamedTemporaryFile(delete=False) as invalid_json:
            path = invalid_json.name

            invalid_json.write(b'Invalid json data')
            invalid_json.close()

            with self.assertRaises(JSONDecodeError):
                load_metadata(path)

            os.remove(invalid_json.name)

    def test_load_metadata_invalid_metadata(self):
        # Todo: this
        schema = {

        }


class TestValidateMetadata(unittest.TestCase):

    def test_validate_metadata_valid_schema(self):

        valid_metadata = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
                "file_data": {
                    "filename": "dummy12345.mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:23"
                }
            },
            "33cb49c54a2bf2f3de62d5f89b31ed042dab57de03e302fef96769ca762cf575": {
                "file_data": {
                    "filename": "Food of the Gods II (1984).mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:24"
                }
            }
        }

        self.assertTrue(validate_metadata(valid_metadata))

    def test_validate_metadata_invalid_hash(self):

        invalid_metadata = {
            "e3b0c44298fc1c149afbf4c8996f": {
                "file_data": {
                    "filename": "dummy12345.mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:23"
                }
            },
            "33cb49c54a2bf2f3de62d5f89b31ed042dab57de03e302fef96769ca762cf575": {
                "file_data": {
                    "filename": "Food of the Gods II (1984).mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:24"
                }
            }
        }

        self.assertFalse(validate_metadata(invalid_metadata))

    def test_validate_metadata_missing_filename(self):

        invalid_metadata = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
                "file_data": {
                    "filename": "dummy12345.mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:23"
                }
            },
            "33cb49c54a2bf2f3de62d5f89b31ed042dab57de03e302fef96769ca762cf575": {
                "file_data": {
                    # "filename": "Food of the Gods II (1984).mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:24"
                }
            }
        }

        self.assertFalse(validate_metadata(invalid_metadata))

    def test_validate_metadata_missing_root(self):

        invalid_metadata = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
                "file_data": {
                    "filename": "dummy12345.mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:23"
                }
            },
            "33cb49c54a2bf2f3de62d5f89b31ed042dab57de03e302fef96769ca762cf575": {
                "file_data": {
                    "filename": "Food of the Gods II (1984).mp4",
                    # "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:24"
                }
            }
        }

        self.assertFalse(validate_metadata(invalid_metadata))

    def test_validate_metadata_missing_timestamp(self):

        invalid_metadata = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
                "file_data": {
                    "filename": "dummy12345.mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    "timestamp": "2023-09-14 04:37:23"
                }
            },
            "33cb49c54a2bf2f3de62d5f89b31ed042dab57de03e302fef96769ca762cf575": {
                "file_data": {
                    "filename": "Food of the Gods II (1984).mp4",
                    "root": "C:/Users/User/Videos/Misc Media/to_sort",
                    # "timestamp": "2023-09-14 04:37:24"
                }
            }
        }

        self.assertFalse(validate_metadata(invalid_metadata))

        # Todo: test cases for metadata title


class TestValidateTimestamp(unittest.TestCase):

    def test_validate_timestamp_valid(self):
        valid_timestamp = '2000-01-01 01:00:00'
        self.assertTrue(validate_timestamp(valid_timestamp))

    def test_validate_timestamp_invalid_format(self):
        invalid_timestamp = '01:00:00 2000-01-01'
        self.assertFalse(validate_timestamp(invalid_timestamp))

