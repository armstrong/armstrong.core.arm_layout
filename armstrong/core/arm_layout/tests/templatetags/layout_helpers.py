from contextlib import contextmanager
from django.template import Context
from django.template import RequestContext
from django.template import Template
from django.template import TemplateDoesNotExist
from django.template import Variable
from django.template.base import VariableDoesNotExist
from django.template.base import TemplateSyntaxError
import fudge
from fudge import Fake, patched_context
from fudge.inspector import arg
import random

from .._utils import TestCase
from ..arm_layout_support.models import Foobar
from ...templatetags import layout_helpers
from ... import utils


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)


def contains_model(test_case, model):
    def test(value):
        test_case.assertTrue("object" in value, msg="sanity check")
        test_case.assertEqual(model, value["object"])
        return True
    return arg.passes_test(test)


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


class get_layout_template_nameTestCase(LayoutHelperTestCase):
    def test_uses_model_name_in_template_name(self):
        random_model_name = "model_name_%d" % random.randint(100, 200)
        model = generate_random_model()
        model._meta.object_name = random_model_name
        result = utils.get_layout_template_name(model, "full_name")
        expected = "layout/arm_layout_support/%s/full_name.html" % (
                random_model_name
        )
        self.assertEqual(result, expected)

    def test_uses_app_label_in_template_name(self):
        random_app_label = "app_label_%d" % random.randint(100, 200)
        model = generate_random_model()
        model._meta.app_label = random_app_label
        result = utils.get_layout_template_name(model, "full_name")
        expected = "layout/%s/foobar/full_name.html" % random_app_label
        self.assertEqual(result, expected)

    def test_uses_name_in_template_name(self):
        random_name = "layout_name_%d" % random.randint(100, 200)
        model = generate_random_model()
        result = utils.get_layout_template_name(model, random_name)
        expected = "layout/arm_layout_support/foobar/%s.html" % random_name
        self.assertEqual(result, expected)


@contextmanager
def stub_render_to_string():
    render_to_string = Fake().is_callable().returns("")
    with patched_context(utils, "render_to_string",
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
    with stub_get_layout_template_name():
        with stub_render_to_string():
            yield


class RenderObjectNodeTestCase(LayoutHelperTestCase):
    def test_dispatches_to_get_layout_template_name(self):
        model = generate_random_model()
        random_name = '"%d"' % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode("object", random_name)

        fake = Fake()
        fake.is_callable().with_args(model, random_name).expects_call()
        with patched_context(utils, "get_layout_template_name", fake):
            with stub_render_to_string():
                node.render(Context({"object": model}))

        fudge.verify()

    def test_uses_the_name_provided_to_init_to_lookup_model(self):
        model = generate_random_model()
        random_object_name = "foo_%d" % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode(random_object_name, "'full_name'")
        with stub_rendering():
            try:
                node.render(Context({random_object_name: model}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")

    def test_passes_request_into_context_if_available(self):
        model = generate_random_model()
        request = self.factory.get("/")
        node = layout_helpers.RenderObjectNode("object", "'show_request'")
        result = node.render(Context({"request": request, "object": model}))

        self.assertRegexpMatches(result, "WSGIRequest")

    def test_does_not_use_RequestContext_by_default(self):
        model = generate_random_model()
        node = layout_helpers.RenderObjectNode("object", "'debug'")
        with self.settings(DEBUG=False):
            result = node.render(Context({"object": model}))
            self.assertEqual(result.strip(), "debug: off")

    def test_uses_RequestContext_if_request_provided(self):
        model = generate_random_model()
        request = self.factory.get("/")
        node = layout_helpers.RenderObjectNode("object", "'debug'")

        with self.settings(DEBUG=True):
            context = RequestContext(request, {"request": request,
                "object": model})
            result = node.render(context)
            self.assertEqual(result.strip(), "debug: on")

    def test_object_is_provided_to_context(self):
        model = generate_random_model()
        context = Context({"object": model})
        with stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            render_to_string.with_args(arg.any(),
                    dictionary=contains_model(self, model),
                    context_instance=context)
            with patched_context(utils, "render_to_string",
                    render_to_string):
                node = layout_helpers.RenderObjectNode("object", "'foobar'")
                result = node.render(context)

    def test_can_pull_object_out_of_complex_context(self):
        model = generate_random_model()
        context = Context({"list": [model]})
        with stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            render_to_string.with_args(arg.any(),
                    dictionary=contains_model(self, model),
                    context_instance=context)
            with patched_context(utils, "render_to_string",
                    render_to_string):
                node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
                result = node.render(context)

    def test_original_context_is_not_contaminated(self):
        model = generate_random_model()
        obj = object()
        context = Context({"object": obj, "list": [model]})
        self.assertEqual(Variable("object").resolve(context), obj,
                msg="sanity check")
        with stub_rendering():
            node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
            result = node.render(context)
        self.assertEqual(Variable("object").resolve(context), obj)


class render_objectTestCase(TestCase):
    def setUp(self):
        self.model = generate_random_model()
        self.string = '{% load layout_helpers %}{% render_object object "full_page" %}'

    @property
    def template(self):
        return Template(self.string)

    @property
    def context(self):
        return Context({"object": self.model})

    @property
    def rendered_template(self):
        return self.template.render(self.context)

    def test_dispatches_to_RenderObjectNode(self):
        self.assertRegexpMatches(self.rendered_template,
                "Title: %s" % self.model.title)

    def test_raises_intelligent_exception_on_error_too_many_parameters(self):
        self.string += "{% render_object object full_page one_to_many %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too many parameters"
        self.assertEqual(e.exception.message, expected)

    def test_raises_intelligent_exception_on_error_too_few_parameters(self):
        self.string += "{% render_object object %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too few parameters"
        self.assertEqual(e.exception.message, expected)

    def test_evaluates_variable_without_quotations(self):
        self.string += '{% render_object object layout_var %}'
        context = self.context
        context["layout_var"] = "full_page"
        self.assertRegexpMatches(self.template.render(context),
                "Title: %s" % self.model.title)

    def test_supports_single_quotes(self):
        self.string = self.string.replace('"', "'")
        self.assertRegexpMatches(self.rendered_template,
                "Title: %s" % self.model.title)
