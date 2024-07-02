import json
import shutil
from json.decoder import JSONDecodeError
import os
import unittest
from unittest.mock import MagicMock, Mock, patch
import tempfile

from main import metadata_save
from main import metadata_load
from main import metadata_validate


# TODO: These metadata tests are no longer needed, but we need to
#       write new tests for the Collection class. We should probably
#       keep these for reference

class TestSaveMetadata(unittest.TestCase):

    def test_save_metadata_valid(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = temp_dir.name
        collection = {'videos': 'test'}
        expected_file_path = os.path.join(path, 'metadata.json')

        metadata_save(collection, path)

        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path, 'r') as temp_file:
            file_content = json.load(temp_file)
            self.assertEqual(collection, file_content)

        temp_dir.cleanup()


class TestLoadMetadata(unittest.TestCase):

    def test_load_metadata_valid(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, 'metadata.json')
        collection = {"videos": "test"}

        with open(path, 'w') as temp_file:
            json.dump(collection, temp_file, indent=4)

        result = metadata_load(path)

        self.assertEqual(collection, result)

        temp_dir.cleanup()

    def test_load_metadata_file_not_found(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, 'metadata.json')

        with self.assertRaises(FileNotFoundError):
            metadata_load(path)

        temp_dir.cleanup()

    def test_load_metadata_invalid_json(self):

        with tempfile.NamedTemporaryFile(delete=False) as invalid_json:
            path = invalid_json.name

            invalid_json.write(b'Invalid json videos')
            invalid_json.close()

            with self.assertRaises(JSONDecodeError):
                metadata_load(path)

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

        self.assertTrue(metadata_validate(valid_metadata))

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

        self.assertFalse(metadata_validate(invalid_metadata))

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

        self.assertFalse(metadata_validate(invalid_metadata))

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

        self.assertFalse(metadata_validate(invalid_metadata))

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

        self.assertFalse(metadata_validate(invalid_metadata))

        # Todo: test cases for metadata title
