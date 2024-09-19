# source/tests/test_service/test_plugin_svc.py

# Standard library
import importlib
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
from tempfile import TemporaryDirectory
import sys

# Local imports
from source.service import plugin_svc as plugin_svc
from source.datasources.base_fetcher import DataFetcher

# Third-party packages


class TestPluginService(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()

        # Simulated package
        self.fake_pkg_name = 'fake_pkg'
        fake_pkg_path = os.path.join(self.temp_dir.name, self.fake_pkg_name)
        self.temp_path = fake_pkg_path
        os.mkdir(fake_pkg_path)
        fake_pkg_init_path = os.path.join(fake_pkg_path, '__init__.py')
        with open(fake_pkg_init_path, 'w') as file:
            file.write('# This file makes the directory a package.')

        # Simulate modules
        self.fake_mod_1_name = 'fake_plugin_1'
        self.fake_mod_2_name = 'fake_plugin_2'
        fake_mod_1_path = os.path.join(fake_pkg_path, self.fake_mod_1_name + '.py')
        fake_mod_2_path = os.path.join(fake_pkg_path, self.fake_mod_2_name + '.py')
        with open(fake_mod_1_path, 'w') as file:
            file.write(
                """from source.datasources.base_fetcher import DataFetcher\nclass FakeAPI1(DataFetcher):\n    def fetch_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")
        with open(fake_mod_2_path, 'w') as file:
            file.write(
                """from source.datasources.base_fetcher import DataFetcher\nclass FakeAPI2(DataFetcher):\n    def fetch_data(self, **kwargs):\n        pass\n    def get_optional_params(self):\n        pass\n    def get_required_params(self):\n        pass""")

        # Prepare path for imports
        sys.path.insert(0, self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        sys.path.pop(0)

    def test_discover_api_classes(self):
        class FakeAPI(DataFetcher):
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

    @patch('source.service.plugin_svc.discover_api_modules')
    def test_discover_plugins(self, mock_discover_api_modules):
        # Arrange
        class FakePlugin(DataFetcher):
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

    def test_get_plugin_instance(self):
        # Arrange
        test_pkg = importlib.import_module(self.fake_pkg_name)
        importlib.reload(test_pkg)  # Avoids using cache with outdated path from other unit tests

        # Act
        result_1 = plugin_svc.get_plugin_instance('FakeAPI1', test_pkg)
        result_2 = plugin_svc.get_plugin_instance('FakeAPI2', test_pkg)

        # Assert
        self.assertIsInstance(result_1, DataFetcher)
        self.assertIsInstance(result_2, DataFetcher)

    def test_get_required_params(self):
        # Arrange
        mock_plugin = Mock()
        mock_plugin.get_required_params.return_value = ['param_1', 'param_2']

        # Act
        result = plugin_svc.get_required_params(mock_plugin)

        # Assert
        self.assertEqual(['param_1', 'param_2'], result)
