# /tests/test_facade/test_session_manager.py

"""
    Unit tests for Facade
"""

# Standard library
from unittest import TestCase
from unittest.mock import Mock
from tempfile import TemporaryDirectory

# Local imports
from source.facade.facade import Facade
from test_state.shared import TestCommand

# Third-party Packages


class TestSessionManager(TestCase):
    def setUp(self) -> None:
        self.session = Facade()
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_clear_staged_operations(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_commit_staged_operations(self):
        # Arrange
        test_cmd_1 = Mock()
        test_cmd_1.exec.return_value = None
        test_cmd_2 = Mock()
        test_cmd_2.exec.return_value = None

        self.session.command_buffer.cmd_buffer.append(test_cmd_1)
        self.session.command_buffer.cmd_buffer.append(test_cmd_2)

        # Act
        self.session.commit_staged_operations()

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

        self.session.command_buffer.cmd_buffer.append(test_cmd_1)
        self.session.command_buffer.cmd_buffer.append(test_cmd_2)

        # Act
        result = self.session.get_preview_of_staged_operations()

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
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_stage_organize_video_files(self):
        # TODO: Implement
        # Arrange
        # Act
        # Assert
        pass

    def test_stage_update_api_metadata(self):
        pass

    def test_undo_transaction(self):
        # Arrange
        test_cmd_1 = TestCommand()
        test_cmd_2 = TestCommand()

        self.session.command_buffer.undo_buffer.append(test_cmd_1)
        self.session.command_buffer.undo_buffer.append(test_cmd_2)

        # Act
        self.session.undo_transaction()

        # Assert
        self.assertTrue(test_cmd_1.undo_called)
        self.assertTrue(test_cmd_2.undo_called)
        self.assertFalse(self.session.command_buffer.undo_buffer)
