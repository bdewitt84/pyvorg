# source/tests/test_service/test_pluginservice.py

# Standard library
import importlib
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory
import sys

# Local imports
from source.api.base_api import BaseAPI
from service import pluginservice as plugin_svc


# Third-party packages


class TestPluginService(TestCase):
    def setUp(self) -> None:
        # self.test_api = TestAPI()
        self.temp_dir = TemporaryDirectory()

        # Simulated package
        self.fake_pkg_name = 'fake_pkg'
        fake_pkg_path = os.path.join(self.temp_dir.name, self.fake_pkg_name)
        self.temp_path = fake_pkg_path
        os.mkdir(fake_pkg_path)
        fake_pkg_init_path = os.path.join(fake_pkg_path, '../test_utils/__init__.py')
        with open(fake_pkg_init_path, 'w') as file:
            file.write('# This file makes the directory a package.')

        # Simulate modules
        self.fake_mod_1_name = 'fake_api_1'
        self.fake_mod_2_name = 'fake_api_2'
        fake_mod_1_path = os.path.join(fake_pkg_path, self.fake_mod_1_name + '.py')
        fake_mod_2_path = os.path.join(fake_pkg_path, self.fake_mod_2_name + '.py')
        with open(fake_mod_1_path, 'w') as file:
            file.write(
                """from source.api.base_api import BaseAPI\nclass FakeAPI1(BaseAPI):\n    def fetch_video_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")
        with open(fake_mod_2_path, 'w') as file:
            file.write(
                """from source.api.base_api import BaseAPI\nclass FakeAPI2(BaseAPI):\n    def fetch_video_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")

        # Prepare path for imports
        sys.path.insert(0, self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        sys.path.pop(0)

    def test_discover_api_classes(self):
        class FakeAPI(BaseAPI):
            pass

        class NotAnAPI:
            pass

        # Arrange
        mod_class_1 = FakeAPI
        mod_class_2 = NotAnAPI

        fake_mod = MagicMock()
        fake_mod.class_1 = mod_class_1
        fake_mod.class_2 = mod_class_2

        # Act
        result = plugin_svc.discover_api_classes(fake_mod)

        # Assert
        self.assertIn('class_1', result.keys())
        self.assertIn(mod_class_1, result.values())
        self.assertNotIn('class_2', result.keys())
        self.assertNotIn(mod_class_2, result.values())

    def test_discover_api_modules(self):
        # Arrange
        test_pkg = importlib.import_module(self.fake_pkg_name)
        importlib.reload(test_pkg)  # Avoids using cache with outdated path from other unit tests

        # Act
        result = plugin_svc.discover_api_modules(test_pkg)

        # Assert
        expected_value = {
            f'{self.fake_pkg_name}.{self.fake_mod_1_name}',
            f'{self.fake_pkg_name}.{self.fake_mod_2_name}'
        }
        self.assertEqual(expected_value, set(result.keys()))
        self.assertTrue(all(mod.__name__ in expected_value for mod in result.values()))

    @patch('source.utils.pluginservice.discover_api_modules')
    def test_discover_plugins(self, mock_discover_api_modules):
        # Arrange
        class FakePlugin(BaseAPI):
            pass

        class NotAPlugin:
            pass

        test_module = MagicMock()
        test_module.plugin_class = FakePlugin
        test_module.not_a_plugin_class = NotAPlugin

        mock_discover_api_modules.return_value = {'test_module': test_module}

        # Act
        result = plugin_svc.discover_plugins(test_module)

        # Assert
        self.assertIn(FakePlugin, result.values())
        self.assertIn('plugin_class', result.keys())
        self.assertNotIn(NotAPlugin, result.values())
        self.assertNotIn('not_a_plugin_class', result.keys())
