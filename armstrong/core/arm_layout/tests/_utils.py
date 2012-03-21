from contextlib import contextmanager
from armstrong.dev.tests.utils.base import ArmstrongTestCase
from django.test.client import RequestFactory
from django.template import Template
import random
import fudge
from fudge import Fake, patched_context
from fudge.inspector import arg

from .arm_layout_support.models import Foobar
from .. import utils
from .. import backends


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)


def contains_model(test_case, model):
    def test(value):
        test_case.assertTrue("object" in value, msg="sanity check")
        test_case.assertEqual(model, value["object"])
        return True
    return arg.passes_test(test)


@contextmanager
def stub_render_to_string():
    render_to_string = Fake().is_callable().returns("")
    with patched_context(backends, "render_to_string",
            render_to_string):
        yield


@contextmanager
def stub_get_layout_template_name():
    get_layout_template_name = Fake().is_callable().returns("")
    with patched_context(utils, "get_layout_template_name",
            get_layout_template_name):
        yield


@contextmanager
def stub_rendering():
    with stub_get_layout_template_name(num_calls=num_calls):
        with stub_render_to_string():
            yield

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

class NodeParsingTestCase(LayoutHelperTestCase):
    @property
    def template(self):
        return Template(self.string)

    @property
    def context(self):
        return Context({"object": self.model})

    @property
    def rendered_template(self):
        return self.template.render(self.context)

