from armstrong.dev.tests.utils.base import ArmstrongTestCase
from django.test.client import RequestFactory
import random

from .arm_layout_support.models import Foobar


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)


class TestCase(ArmstrongTestCase):
    def setUp(self):
        self.factory = RequestFactory()


class LayoutHelperTestCase(TestCase):
    def setUp(self):
        super(LayoutHelperTestCase, self).setUp()
        m = Foobar()
        self._original_object_name = m._meta.object_name
        self._original_app_label = m._meta.app_label

    def tearDown(self):
        m = Foobar()
        m._meta.object_name = self._original_object_name
        m._meta.app_label = self._original_app_label
        super(LayoutHelperTestCase, self).tearDown()
