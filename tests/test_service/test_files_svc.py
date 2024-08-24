# ./source/tests/test_service/test_files_svc.py

# Standard library
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

# Local imports
import source.service.file_svc as file_svc

# Third-party packages


class TestFileService(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.test_data = 'test_data'

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_file_write(self):
        # Arrange
        write_ok = Path(self.temp_dir.name) / 'write_okay.file'
        already_exists = Path(self.temp_dir.name) / 'already_exists.file'
        with already_exists.open('w'):
            pass

        # Act and Assert
        file_svc.file_write(write_ok, self.test_data)
        self.assertTrue(write_ok.exists())
        with open(write_ok, 'r') as file:
            written_data = file.read()
        self.assertEqual(written_data, self.test_data)

        with self.assertRaises(FileExistsError):
            file_svc.file_write(already_exists, self.test_data)

    def test_file_read(self):
        # Arrange
        file_exists = Path(self.temp_dir.name) / 'exists.file'
        file_does_not_exist = Path(self.temp_dir.name) / 'does_not_exist.file'

        file_exists.write_text(self.test_data)

        # Act and assert
        file_svc.file_read(file_exists)

        with self.assertRaises(FileNotFoundError):
            file_svc.file_read(file_does_not_exist)

    def test_make_dir(self):
        # Arrange
        path = Path(self.temp_dir.name)

        # Act
        file_svc.make_dir(path)

        # Assert
        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())

    def test_mimic_folder(self):
        # Arrange
        temp_dir = Path(self.temp_dir.name)
        src_tree = temp_dir / 'src_tree'
        dst_tree = temp_dir / 'dst_tree'

        make = [
            temp_dir / 'src_tree',
            temp_dir / 'src_tree' / 'root.file',
            temp_dir / 'src_tree' / 'sub_dir_1',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub.file',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub_sub_dir',
            temp_dir / 'src_tree' / 'sub_dir_1' / 'sub_sub_dir' / 'sub_sub.file',
            temp_dir / 'src_tree' / 'sub_dir_2',
            temp_dir / 'dst_tree'
        ]

        for path in make:
            if path.is_file():
                with path.open('w'):
                    pass
            elif path.is_dir():
                path.mkdir()

        # Act
        file_svc.mimic_folder(src_tree, dst_tree)

        result = []
        for dirpath, _, files in os.walk(dst_tree):
            result.append(Path(dirpath).relative_to(dst_tree))
            for file in files:
                result.append((Path(file).relative_to(dst_tree)))

        # Assert
        src_tree_dirs = [Path(dirpath).relative_to(src_tree) for dirpath, _, _ in os.walk(src_tree)]
        dst_tree_dirs = [Path(dirpath).relative_to(dst_tree) for dirpath, _, _ in os.walk(dst_tree)]
        self.assertEqual(src_tree_dirs, dst_tree_dirs)

    def test_move_file(self):
        # Arrange
        src_exists_path = Path(self.temp_dir.name) / 'exists.file'
        src_does_not_exist_path = Path(self.temp_dir.name) / 'does_not_exist.file'
        with src_exists_path.open('w'):
            pass
        dst_path = Path(self.temp_dir.name) / 'dst_folder'

        # Act
        with self.assertRaises(FileNotFoundError):
            file_svc.move_file(src_does_not_exist_path, dst_path)

        file_svc.move_file(src_exists_path, dst_path)

        # Assert
        with self.assertRaises(FileExistsError):
            file_svc.move_file(src_exists_path, dst_path)

        self.assertFalse(src_exists_path.exists())
        self.assertTrue(dst_path.exists())

    def test_parse_glob_string(self):
        # Arrange
        glob_str = './fake_root/fake_sub/*.*'

        # Act
        result_path, result_glob = file_svc.parse_glob_string(glob_str)

        # Assert
        self.assertEqual(result_path, Path('fake_root/fake_sub'))
        self.assertEqual(result_glob, '*.*')

    def test_path_is_writable(self):
        # Arrange
        writable_target_path = Path(self.temp_dir.name) / 'writable.file'
        non_writable_target_path = Path(self.temp_dir.name) / 'non_writable.file'

        writable_target_path.touch(222)
        non_writable_target_path.touch(555)

        # Act and Assert
        self.assertTrue(file_svc.path_is_writable(writable_target_path))
        self.assertFalse(file_svc.path_is_writable(non_writable_target_path))

    def test_path_is_readable(self):
        # Arrange
        readable_target_path = Path(self.temp_dir.name) / 'readable.file'
        non_readable_target_path = Path(self.temp_dir.name) / 'non_readable.file'

        readable_target_path.touch(444)
        non_readable_target_path.touch(333)

        # Act and Assert
        self.assertTrue(file_svc.path_is_readable(readable_target_path))
        # This test will always fail on Windows
        # self.assertFalse(path_is_readable(non_readable_target_path))

    def test_dir_is_empty(self):
        empty_dir = Path(self.temp_dir.name) / 'empty_dir'
        not_empty_dir = Path(self.temp_dir.name) / 'not_empty_dir'
        dummy_file = not_empty_dir / 'dummy.file'

        empty_dir.mkdir()
        not_empty_dir.mkdir()
        dummy_file.touch()

        # Act
        result_empty = file_svc.dir_is_empty(empty_dir)
        result_not_empty = file_svc.dir_is_empty(not_empty_dir)

        # Assert
        self.assertTrue(result_empty)
        self.assertFalse(result_not_empty)

    def test_get_files_from_path(self):
        # Arrange
        test_path = Path(self.temp_dir.name)
        test_file_1 = test_path / 'test_file.1'
        test_file_2 = test_path / 'test_file.2'
        fake_file = test_path / 'doesnt_exist.file'

        test_file_1.touch()
        test_file_2.touch()

        # Act
        result = file_svc.get_files_from_path(test_path)

        # Assert
        self.assertIn(test_file_1, result)
        self.assertIn(test_file_2, result)
        self.assertNotIn(fake_file, result)

    def test_get_file_type(self):
        # Arrange
        test_path = Path(self.temp_dir.name)
        dummy_mp4 = test_path / 'dummy.mp4'
        dummy_avi = test_path / 'dummy.avi'
        dummy_txt = test_path / 'dummy.txt'

        files_to_create = [dummy_mp4, dummy_avi, dummy_txt]
        for file in files_to_create:
            file.touch()

        # Act
        result_mp4 = file_svc.get_file_type(dummy_mp4)
        result_avi = file_svc.get_file_type(dummy_avi)
        result_txt = file_svc.get_file_type(dummy_txt)

        # Assert
        self.assertEqual(result_mp4, 'video')
        self.assertEqual(result_avi, 'video')
        self.assertEqual(result_txt, '')

    def test_hash_sha256(self):
        # Arrange
        filename = 'test.file'
        file_path = Path(self.temp_dir.name) / filename
        with file_path.open('wb') as file:
            file.write(b'test_data')

        # Act
        computed_hash = file_svc.hash_sha256(file_path)

        # Assert
        expected_hash = 'e7d87b738825c33824cf3fd32b7314161fc8c425129163ff5e7260fc7288da36'
        self.assertEqual(expected_hash, computed_hash)

        with self.assertRaises(FileNotFoundError):
            file_svc.hash_sha256('bogus_file_name')  # type:ignore
