# ./source/facade/requestparser.py

"""

"""

# Standard library
# n/a

# Local imports
from source.utils import serviceutils

# Third-party packages
# n/a


class RequestParser:
    def __init__(self):
        self.service_to_invoke = None

    def parse(self, service_name: str, *args, **kwargs):
        self._get_service_instance(service_name)
        self._invoke_service(args, kwargs)

    def _get_service_instance(self, service_name: str):
        self.service_to_invoke = serviceutils.get_service_instance(service_name)

    def _invoke_service(self, args, kwargs):
        self.service_to_invoke.call(*args, **kwargs)
