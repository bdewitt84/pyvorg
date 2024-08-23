# ./source/tests/test_service/test_fileservice.py

# Standard library
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, patch, Mock

# Local imports
import source.service.fileservice as file_svc

# Third-party packages


class TestFileService(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_(self):
        # Arrange

        # Act

        # Assert
        pass
