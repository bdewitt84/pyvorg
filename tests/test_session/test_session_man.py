# /tests/test_session/test_session_manager.py

"""
    Unit tests for SessionManager
"""

# Standard library
import os
from unittest import TestCase
from unittest.mock import Mock
from tempfile import TemporaryDirectory
import pickle

# Local imports
import source.api.api_manager
import source.collection.col
import source.command.combuffer
from source.session.session_man import SessionManager
from tests.test_command.shared import TestCommand

# Third-party Packages


class TestSessionManager(TestCase):
    def setUp(self) -> None:
        self.session = SessionManager()
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_commit_transaction(self):
        # Arrange
        test_cmd_1 = Mock()
        test_cmd_1.exec.return_value = None
        test_cmd_2 = Mock()
        test_cmd_2.exec.return_value = None

        self.session.cb.cmd_buffer.append(test_cmd_1)
        self.session.cb.cmd_buffer.append(test_cmd_2)

        # Act
        self.session.commit_transaction()

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
    #     self.assertTrue('col' in result.__dict__)
    #     self.assertTrue('cb' in result.__dict__)
    #     self.assertTrue('apiman' in result.__dict__)
    #     self.assertEqual(type(result.col), source.collection.col.Collection)
    #     self.assertEqual(type(result.cb), source.command.combuffer.CommandBuffer)
    #     self.assertEqual(type(result.apiman), source.api.api_manager.APIManager)

    def test_preview_transaction(self):
        # Arrange
        test_cmd_1 = Mock()
        test_cmd_1.__str__ = lambda x: 'Test cmd 1'
        test_cmd_2 = Mock()
        test_cmd_2.__str__ = lambda x: 'Test cmd 2'

        self.session.cb.cmd_buffer.append(test_cmd_1)
        self.session.cb.cmd_buffer.append(test_cmd_2)

        # Act
        result = self.session.get_transaction_preview()

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
    #     self.assertTrue('col' in result.__dict__)
    #     self.assertTrue('cb' in result.__dict__)
    #     self.assertTrue('apiman' in result.__dict__)
    #     self.assertEqual(type(result.col), source.collection.col.Collection)
    #     self.assertEqual(type(result.cb), source.command.combuffer.CommandBuffer)
    #     self.assertEqual(type(result.apiman), source.api.api_manager.APIManager)

    def test_undo_transaction(self):
        # Arrange
        test_cmd_1 = TestCommand()
        test_cmd_2 = TestCommand()

        self.session.cb.undo_buffer.append(test_cmd_1)
        self.session.cb.undo_buffer.append(test_cmd_2)

        # Act
        self.session.undo_transaction()

        # Assert
        self.assertTrue(test_cmd_1.undo_called)
        self.assertTrue(test_cmd_2.undo_called)
        self.assertFalse(self.session.cb.undo_buffer)
