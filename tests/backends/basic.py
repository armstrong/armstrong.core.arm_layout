from armstrong.core.arm_layout.backends import BasicLayoutBackend
from .._utils import TestCase
from ._common import BackendTestCaseMixin


class BasicLayoutBackendTestCase(BackendTestCaseMixin, TestCase):
    backend_class = BasicLayoutBackend
