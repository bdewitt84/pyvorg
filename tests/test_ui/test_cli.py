# ./tests/test_ui/test_ui.py

"""
    Unit tests for ui.py
"""
# Standard library
from tempfile import TemporaryDirectory
from unittest import TestCase

# Local imports
from source.facade.facade import Facade

# Third-party packages


class TestUI(TestCase):
    def setUp(self) -> None:
        self.test_dir = TemporaryDirectory()
        self.session = Facade()

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
