# /tests/test_facade/test_pyvorg_facade.py

"""
    Unit tests for Facade
"""

# Standard library
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, Mock
from tempfile import TemporaryDirectory

# Local imports
from source.facade.pyvorg_facade import Facade
from source.state.col import Collection
from source.state.combuffer import CommandBuffer
from source.utils.helper import create_dummy_files
from tests.test_state.shared import FauxCmd

from source.state.update_video_data import UpdateVideoData
from source.state.move_video import MoveVideo

# Third-party Packages
# n/a


class TestFacade(TestCase):
    def setUp(self) -> None:
        self.collection = Collection()
        self.command_buffer = CommandBuffer()
        self.facade = Facade(self.collection, self.command_buffer)
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_clear_staged_operations(self):
        # Arrange
        mock_cmd_1 = FauxCmd()
        mock_cmd_2 = FauxCmd()
        self.command_buffer.add_command(mock_cmd_1)
        self.command_buffer.add_command(mock_cmd_2)

        # Act
        self.facade.clear_staged_operations()

        # Assert
        self.assertTrue(self.command_buffer.exec_is_empty())

    def test_commit_staged_operations(self):
        # Arrange
        test_cmd_1 = Mock()
        test_cmd_1.exec.return_value = None
        test_cmd_2 = Mock()
        test_cmd_2.exec.return_value = None

        self.facade.command_buffer.cmd_buffer.append(test_cmd_1)
        self.facade.command_buffer.cmd_buffer.append(test_cmd_2)

        # Act
        self.facade.commit_staged_operations()

        # Assert
        test_cmd_1.exec.assert_called_once()
        test_cmd_2.exec.assert_called_once()

    def test_export_collection_metadata(self):
        pass

    def test_preview_of_staged_operations(self):
        # Arrange
        test_cmd_1 = Mock()
        test_cmd_1.__str__ = lambda x: 'Test cmd 1'
        test_cmd_2 = Mock()
        test_cmd_2.__str__ = lambda x: 'Test cmd 2'

        self.facade.command_buffer.cmd_buffer.append(test_cmd_1)
        self.facade.command_buffer.cmd_buffer.append(test_cmd_2)

        # Act
        result = self.facade.get_preview_of_staged_operations()

        # Assert
        self.assertTrue('Test cmd 1' in result)
        self.assertTrue('Test cmd 2' in result)

    def test_import_collections_metadata(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_scan_files_in_path(self):
        # Arrange
        scan_path = Path(self.temp_dir.name)
        files = create_dummy_files(scan_path, 3, lambda x: 'dummy_' + str(x) + '.mp4')

        # Act
        self.facade.scan_files_in_path(str(scan_path))

        # Assert
        paths = [video.get_path() for video in self.collection.get_videos()]

        self.assertIn(files[0], paths)
        self.assertIn(files[1], paths)
        self.assertIn(files[2], paths)
        self.assertNotIn('fake_ass_file', paths)

    def test_stage_organize_video_files(self):
        # Arrange
        source_path = Path(self.temp_dir.name)
        files = create_dummy_files(source_path, 3, lambda x: 'dummy_' + str(x) + '.mp4')
        added_vids = self.collection.add_files(files)
        for vid, path, num in zip(added_vids, files, range(3)):
            vid.data.update({
                'user_data': {
                    'path': path,
                    'title': path.stem,
                    'year': str(num)
                }
            })

        dest_path = Path(self.temp_dir.name) / 'dest'

        # Act
        self.facade.stage_organize_video_files(str(dest_path))

        # Assert
        videos = self.collection.get_videos()
        cmds: list[MoveVideo] = self.command_buffer._get_commands()

        self.assertEqual(3, len(cmds))

        for cmd in cmds:
            self.assertIn(cmd.video, videos)
            self.assertIn(cmd.origin_dir, files)

    @patch('source.service.plugin_svc.get_plugin_instance')
    def test_stage_update_api_metadata(self, mock_get_plugin_instance):
        # Arrange
        files = create_dummy_files(self.temp_dir.name, 3, lambda x: 'dummy_' + str(x) + '.mp4')
        self.collection.add_files(files)

        mock_plugin = Mock()
        mock_plugin.get_required_params.return_value = ['filename', 'path']

        mock_get_plugin_instance.return_value = mock_plugin

        # Act
        self.facade.stage_update_api_metadata('plugin_name')

        # Assert
        videos = self.collection.get_videos()
        cmds: list[UpdateVideoData] = self.command_buffer._get_commands()

        self.assertEqual(3, len(cmds))

        for cmd in cmds:
            self.assertIn(cmd.video, videos)
            self.assertEqual(cmd.api, mock_plugin)
            self.assertIn('filename', cmd.kwargs.keys())
            self.assertIn('path', cmd.kwargs.keys())

    def test_undo_transaction(self):
        # Arrange
        test_cmd_1 = FauxCmd()
        test_cmd_2 = FauxCmd()

        self.facade.command_buffer.undo_buffer.append(test_cmd_1)
        self.facade.command_buffer.undo_buffer.append(test_cmd_2)

        # Act
        self.facade.undo_transaction()

        # Assert
        self.assertTrue(test_cmd_1.undo_called)
        self.assertTrue(test_cmd_2.undo_called)
        self.assertFalse(self.facade.command_buffer.undo_buffer)
