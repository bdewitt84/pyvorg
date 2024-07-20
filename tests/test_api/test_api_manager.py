# /tests/api/api_manager.py

# Standard library
from unittest import TestCase
from unittest.mock import MagicMock, patch

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

    def tearDown(self) -> None:
        pass

    def test_discover_api_classes(self):

        # Arrange
        fake_api_mod = MagicMock()
        fake_api_mod.FakeAPI1 = FakeAPI1
        fake_api_mod.FakeAPI2 = FakeAPI2
        api_mods = [
            ('fake_mod_1', fake_api_mod),
        ]

        # Act
        result = self.test_api_man.discover_api_classes(api_mods)

        # Assert
        expected_value = {
            FakeAPI1.__name__: fake_api_mod.FakeAPI1,
            FakeAPI2.__name__: fake_api_mod.FakeAPI2
        }
        self.assertEqual(expected_value, result)

    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_discover_api_modules(self, mock_iter_modules, mock_import_module):

        # Arrange
        fake_api_1_name = 'source.api.fake_api_1'
        fake_api_2_name = 'source.api.fake_api_2'
        mock_iter_modules.return_value = [
            (None, fake_api_1_name, False),
            (None, fake_api_2_name, False)
        ]
        mock_import_module.side_effect = lambda name: MagicMock(__name__=name)

        # Act
        result = self.test_api_man.discover_api_modules()

        # Assert
        expected_value = {fake_api_1_name, fake_api_2_name}
        self.assertEqual(expected_value, result.keys())
        self.assertEqual(result.get(fake_api_1_name).__name__, fake_api_1_name)
        self.assertEqual(result.get(fake_api_2_name).__name__, fake_api_2_name)

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

    def test_register_apis(self):
        # Arrange
        apis = {
            FakeAPI1.__name__: FakeAPI1,
            FakeAPI2.__name__: FakeAPI2
        }

        # Act
        self.test_api_man.register_apis(apis)

        # Assert
        self.assertTrue(FakeAPI1.__name__ in self.test_api_man.apis)
        self.assertTrue(FakeAPI2.__name__ in self.test_api_man.apis)
        self.assertTrue(self.test_api_man.apis.get(FakeAPI1.__name__), FakeAPI1)
        self.assertTrue(self.test_api_man.apis.get(FakeAPI2.__name__), FakeAPI2)
