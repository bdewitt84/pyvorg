# ./tests/test_cli/test_ui.py

"""
    Unit tests for ui.py
"""
import os
# Standard library
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

# Local imports
import source.ui.cli as ui
import source.collection.col
from source.session.pyvorg_session import PyvorgSession

# Third-party packages


class TestUI(TestCase):
    def setUp(self) -> None:
        self.test_dir = TemporaryDirectory()
        self.session = PyvorgSession()

    def tearDown(self) -> None:
        self.test_dir.cleanup()

    def test_handle_args_commit(self):
        pass

    def test_handle_args_export(self):
        pass

    def test_handle_args_fetch(self):
        pass

    def test_handle_organize(self):
        pass

    def test_handle_args_profile(self):
        pass

    def test_handle_args_undo(self):
        pass

    def test_handle_args_view(self):
        pass

    def test_parse_args(self):
        pass
