# /tests/api/api_manager.py
import importlib
import os
# Standard library
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch
import sys

# Local imports
from source.api.api_manager import APIManager
from source.api.base_api import BaseAPI

# Third-party packages


class FakeAPI1(BaseAPI):
    def fetch_video_data(self, **kwargs):
        pass

    def get_optional_params(self):
        pass

    def get_required_params(self):
        pass


class FakeAPI2(BaseAPI):
    def fetch_video_data(self, **kwargs):
        pass

    def get_optional_params(self):
        pass

    def get_required_params(self):
        pass


class TestAPI(BaseAPI):

    def __init__(self):
        super().__init__()

    def fetch_video_data(self, **kwargs):
        return {'test_key': 'test_value'}

    def get_name(self):
        return 'test_api'

    def get_optional_params(self):
        return ['optional_param_1', 'optional_param_2']

    def get_required_params(self):
        return ['required_param_1', 'required_param_2']


class TestAPIManager(TestCase):

    def setUp(self) -> None:
        self.test_api_man = APIManager()
        self.test_api = TestAPI()
        self.temp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_discover_api_classes(self):

        # Arrange
        fake_api_mod = MagicMock()
        fake_api_mod.FakeAPI1 = FakeAPI1
        fake_api_mod.FakeAPI2 = FakeAPI2

        # Act
        result = self.test_api_man.discover_api_classes(fake_api_mod)

        # Assert
        expected_value = {
            FakeAPI1.__name__: fake_api_mod.FakeAPI1,
            FakeAPI2.__name__: fake_api_mod.FakeAPI2
        }
        self.assertEqual(expected_value, result)

    def test_discover_api_modules(self):
        # Arrange - simulate package
        fake_pkg_name = 'fake_pkg'
        fake_pkg_path = os.path.join(self.temp_dir.name, fake_pkg_name)
        os.mkdir(fake_pkg_path)
        fake_pkg_init_path = os.path.join(fake_pkg_path, '__init__.py')
        with open(fake_pkg_init_path, 'w') as file:
            file.write('# This file makes the directory a package.')

        # Arrange - simulate modules
        fake_mod_1_name = 'fake_api_1'
        fake_mod_2_name = 'fake_api_2'
        fake_mod_1_path = os.path.join(fake_pkg_path, fake_mod_1_name + '.py')
        fake_mod_2_path = os.path.join(fake_pkg_path, fake_mod_2_name + '.py')
        with open(fake_mod_1_path, 'w') as file:
            file.write(
                """from source.api.base_api import BaseAPI\nclass FakeAPI1(BaseAPI):\n    def fetch_video_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")
        with open(fake_mod_2_path, 'w') as file:
            file.write(
                """from source.api.base_api import BaseAPI\nclass FakeAPI2(BaseAPI):\n    def fetch_video_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")

        # Arrange - import simulated package
        sys.path.insert(0, self.temp_dir.name)
        test_pkg = importlib.import_module(fake_pkg_name)

        # Act
        result = self.test_api_man.discover_api_modules(test_pkg)

        # Assert
        expected_value = {f'{fake_pkg_name}.{fake_mod_1_name}', f'{fake_pkg_name}.{fake_mod_2_name}'}
        self.assertEqual(expected_value, set(result.keys()))
        self.assertTrue(all(mod.__name__ in expected_value for mod in result.values()))

        sys.path.pop(0)

    def test_get_api_list(self):
        # Arrange
        self.test_api_man.apis.update({self.test_api.get_name(): self.test_api})

        # Act
        result = self.test_api_man.get_api_list()

        # Assert
        expected_value = [self.test_api]
        self.assertEqual(expected_value, result)

    def test_get_api_names(self):
        # Arrange
        self.test_api_man.apis.update({'test_name': self.test_api})

        # Act
        result = self.test_api_man.get_api_names()

        # Assert
        expected_value = ['test_name']
        self.assertEqual(expected_value, result)

    def test_register_api(self):
        # Arrange

        # Act
        self.test_api_man.register_api(FakeAPI1.__name__, FakeAPI1)
        self.test_api_man.register_api(FakeAPI2.__name__, FakeAPI2)

        # Assert
        self.assertTrue(FakeAPI1.__name__ in self.test_api_man.apis)
        self.assertTrue(FakeAPI2.__name__ in self.test_api_man.apis)
        self.assertTrue(isinstance(self.test_api_man.apis.get(FakeAPI1.__name__), FakeAPI1))
        self.assertTrue(isinstance(self.test_api_man.apis.get(FakeAPI2.__name__), FakeAPI2))
