# tests/test_helper.py

"""
Unit tests for source/helper.py
"""
import os
# Standard library
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Local imports
from source.constants import *
from source.helper import *
from source.video import Video


class TestAddVideo(unittest.TestCase):

    def test_add_video_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'Test videos')
            temp_file.close()

            collection = {}
            path = temp_file.name

            expected_hash = hash_sha256(path)
            # expected_timestamp = generate_timestamp()

            add_video(collection, path)

            self.assertIn(expected_hash, collection)
            self.assertEqual(collection[expected_hash][FILE_DATA][FILENAME], os.path.basename(path))
            self.assertEqual(collection[expected_hash][FILE_DATA][ROOT], os.path.dirname(path))
            self.assertTrue(timestamp_validate(collection[expected_hash][FILE_DATA][TIMESTAMP]))
            # self.assertEqual(collection[expected_hash][FILE_DATA][TIMESTAMP], expected_timestamp)


class TestClassName(unittest.TestCase):

    def test_class_name(self):
        integer = 1
        string = 'string'
        boolean = True
        none = None

        self.assertEqual('int', class_name(integer))
        self.assertEqual('str', class_name(string))
        self.assertEqual('bool', class_name(boolean))
        self.assertEqual('NoneType', class_name(none))

# TODO: Rewrite test for Video.generate_dir_name()
# class TestGenerateVideoDirName(unittest.TestCase):
#
#     @staticmethod
#     def mock_get_data(key, default='unknown'):
#         data = default
#         if key == 'year':
#             data = 'expected year'
#         return data
#
#
#     @patch('video.Video.get_data',
#            side_effect=lambda key, default='expected default': TestGenerateVideoDirName.mock_get_data(key, default)
#            )
#     def test_generate_video_dir_name(self, mock_get_data):
#         temp_dir = tempfile.TemporaryDirectory()
#         temp_video_path = temp_dir.name + 'temp_vid.mp4'
#
#         with open(temp_video_path, 'w') as temp_file:
#             temp_file.write('test_data')
#             temp_file.close()
#
#         with open(temp_video_path, 'r') as temp_file:
#             video = Video()
#             video.update_file_data(temp_file.name)
#             format_str = '%title (%year)'
#             _, default_title = FORMAT_SPECIFIERS.get('%title')
#             expected_str = default_title + ' (expected year)'
#             result = generate_video_dir_name(video, format_str)
#             self.assertEqual(expected_str, result)
#
#         temp_dir.cleanup()


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


class HashSHA256(unittest.TestCase):

    def test_hash_sha256_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'test_data')
            temp_file.close()

            expected_hash = 'e7d87b738825c33824cf3fd32b7314161fc8c425129163ff5e7260fc7288da36'
            computed_hash = hash_sha256(temp_file.name)

            os.remove(temp_file.name)

            self.assertEqual(expected_hash, computed_hash)

    def test_hash_sha256_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            hash_sha256('bogus_file_name')


# TODO: Rewrite for Collection.scan_directory()
# class TestScanDirectory(unittest.TestCase):
#
#     def setUp(self) -> None:
#         self.collection = {}
#         self.temp_dir = tempfile.TemporaryDirectory()
#
#         test_files = ['video1.mp4', 'video2.mkv', 'notavideo.txt']
#         for filename in test_files:
#             path = os.path.join(self.temp_dir.name, filename)
#             with open(path, 'w') as file:
#                 file.write(filename)  # We use unique videos to produce unique hashes
#
#     def tearDown(self) -> None:
#         self.temp_dir.cleanup()
#
#     def test_scan_directory_valid(self):
#         mock_add_video = MagicMock()
#
#         with unittest.mock.patch('helper.add_video', mock_add_video):
#             scan_directory(self.collection, self.temp_dir.name)
#
#         self.assertEqual(mock_add_video.call_count, 2)


class TestTimestampValidate(unittest.TestCase):

    def test_timestamp_validate_valid(self):
        valid_timestamp = '2000-01-01 01:00:00'
        self.assertTrue(timestamp_validate(valid_timestamp))

    def test_timestamp_validate_invalid_format(self):
        invalid_timestamp = '01:00:00 2000-01-01'
        self.assertFalse(timestamp_validate(invalid_timestamp))


class TestFileWrite(unittest.TestCase):

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.test_data = 'test data'

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_file_write_valid(self):
        filename = 'doesnt_exist'
        path = os.path.join(self.dir.name, filename)
        file_write(path, self.test_data)

        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as file:
            written = file.read()
        self.assertEqual(written, self.test_data)

    def test_file_write_file_exists(self):
        filename = 'exists'
        path = os.path.join(self.dir.name, filename)
        if os.path.exists(path):
            raise FileExistsError(f"The file '{path}' already exists. Test file cannot be written")
        with open(path, 'w') as file:
            file.write(self.test_data)

        with self.assertRaises(FileExistsError):
            file_write(path, self.test_data)
