from armstrong.dev.tests.utils.base import ArmstrongTestCase
from django.test.client import RequestFactory

class TestCase(ArmstrongTestCase):
    def setUp(self):
        self.factory = RequestFactory()
