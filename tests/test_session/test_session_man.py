# /tests/test_session/test_session_manager.py

"""
    Unit tests for PyvorgSession
"""

# Standard library
import os
from unittest import TestCase
from unittest.mock import Mock
from tempfile import TemporaryDirectory

# Local imports
from source.facade.pyvorg_session import PyvorgSession
from tests.test_command.shared import TestCommand

# Third-party Packages


class TestSessionManager(TestCase):
    def setUp(self) -> None:
        self.session = PyvorgSession()
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_commit_transaction(self):
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

    # def test_pickle_session(self):
    #     # Arrange
    #     filename = 'test.pickle'
    #     path = os.path.join(self.temp_dir.name, filename)
    #
    #     # Act
    #     self.session.pickle_session(path)
    #
    #     # Assert
    #     with open(path, 'rb') as file:
    #         result = pickle.load(file)
    #
    #     video.assertTrue('collection' in result.__dict__)
    #     video.assertTrue('command_buffer' in result.__dict__)
    #     video.assertTrue('api_manager' in result.__dict__)
    #     video.assertEqual(type(result.collection), source.collection.collection.Collection)
    #     video.assertEqual(type(result.command_buffer), source.command.combuffer.CommandBuffer)
    #     video.assertEqual(type(result.api_manager), source.api.api_manager.APIManager)

    def test_preview_transaction(self):
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

    def test_scan_path(self):
        pass

    def test_stage_organize_video_files(self):
        pass

    def test_stage_update_api_metadata(self):
        pass

    # def test_unpickle_session(self):
    #     # Arrange
    #     filename = 'test.pickle'
    #     path = os.path.join(self.temp_dir.name, filename)
    #     with open(path, 'wb') as file:
    #         pickle.dump(self.session, file)
    #
    #     # Act
    #     result = SessionManager.unpickle_session(path)
    #
    #     # Assert
    #     video.assertTrue('collection' in result.__dict__)
    #     video.assertTrue('command_buffer' in result.__dict__)
    #     video.assertTrue('api_manager' in result.__dict__)
    #     video.assertEqual(type(result.collection), source.collection.collection.Collection)
    #     video.assertEqual(type(result.command_buffer), source.command.combuffer.CommandBuffer)
    #     video.assertEqual(type(result.api_manager), source.api.api_manager.APIManager)

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
