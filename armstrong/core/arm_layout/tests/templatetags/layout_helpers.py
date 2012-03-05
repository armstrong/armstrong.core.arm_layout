import re
import string
import random
import fudge
from fudge.inspector import arg
from contextlib import contextmanager

from django.template import (
    Template, Context, RequestContext, NodeList, Variable,
    TemplateDoesNotExist, TemplateSyntaxError, VariableDoesNotExist)
from django.test.client import RequestFactory

from ..arm_layout_support.models import Foobar
from ...templatetags.layout_helpers import (
    RenderObjectNode, RenderListNode, RenderIterNode,
    RenderNextNode, RenderRemainderNode)
from ... import utils
from .._utils import TestCase


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)


@contextmanager
def stub_render_to_string():
    render_to_string = fudge.Fake().is_callable().returns("")
    with fudge.patched_context(utils, "render_to_string",
            render_to_string):
        yield


@contextmanager
def stub_get_layout_template_name():
    get_layout_template_name = fudge.Fake().is_callable().returns("")
    with fudge.patched_context(utils, "get_layout_template_name",
         get_layout_template_name):
        yield


class RenderObjectNodeTestCase(TestCase):
    def setUp(self):
        super(RenderObjectNodeTestCase, self).setUp()
        self.factory = RequestFactory()
        self.model = generate_random_model()

    def contains_model(self, model):
        def test(value):
            self.assertTrue("object" in value, msg="sanity check")
            self.assertEqual(model, value["object"])
            return True
        return arg.passes_test(test)

    def test_dispatches_to_get_layout_template_name(self):
        random_name = '"%d"' % random.randint(100, 200)
        node = RenderObjectNode("object", random_name)

        fake = fudge.Fake()
        fake.is_callable().with_args(self.model, random_name).expects_call()
        with fudge.patched_context(utils, "get_layout_template_name", fake):
            with stub_render_to_string():
                node.render(Context({"object": self.model}))

        fudge.verify()

    def test_uses_the_name_provided_to_init_to_lookup_model(self):
        random_object_name = "foo_%d" % random.randint(100, 200)
        node = RenderObjectNode(random_object_name, "'full_name'")

        with stub_render_to_string():
            try:
                node.render(Context({random_object_name: self.model}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")

    def test_passes_request_into_context_if_available(self):
        request = self.factory.get("/")
        node = RenderObjectNode("object", "'show_request'")
        result = node.render(Context({"request": request, "object": self.model}))

        self.assertRegexpMatches(result, "WSGIRequest")

    def test_does_not_use_RequestContext_by_default(self):
        node = RenderObjectNode("object", "'debug'")
        with self.settings(DEBUG=False):
            result = node.render(Context({"object": self.model}))
            self.assertEqual(result.strip(), "debug: off")

    def test_uses_RequestContext_if_request_provided(self):
        request = self.factory.get("/")
        node = RenderObjectNode("object", "'debug'")

        with self.settings(DEBUG=True):
            context = RequestContext(request, {"object": self.model})
            result = node.render(context)
            self.assertEqual(result.strip(), "debug: on")

    def test_object_is_provided_to_context(self):
        context = Context({"object": self.model})

        with stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            node = RenderObjectNode("object", "'foobar'")
            render_to_string.with_args(
                arg.any(),
                dictionary=self.contains_model(self.model),
                context_instance=context)
            with fudge.patched_context(utils, "render_to_string", render_to_string):
                node.render(context)

    def test_can_pull_object_out_of_complex_context(self):
        context = Context({"list": [self.model]})
        with stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            node = RenderObjectNode("list.0", "'foobar'")
            render_to_string.with_args(
                arg.any(),
                dictionary=self.contains_model(self.model),
                context_instance=context)
            with fudge.patched_context(utils, "render_to_string", render_to_string):
                node.render(context)

    def test_original_context_is_not_contaminated(self):
        obj = object()
        context = Context({"object": obj, "list": [self.model]})
        self.assertEqual(Variable("object").resolve(context), obj,
                msg="sanity check")
        with stub_render_to_string():
            node = RenderObjectNode("list.0", "'foobar'")
            node.render(context)
        self.assertEqual(Variable("object").resolve(context), obj)


class render_modelTestCase(TestCase):
    def setUp(self):
        self.model = generate_random_model()
        self.string = ""
        self.tpl_name = "full_page"
        self.context = Context({"object": self.model})
        self.expected_result = "Title: %s" % self.model.title

    def make_str(self, str, **kwargs):
        self.string = string.Template(str).substitute(**kwargs)

    @property
    def rendered_template(self):
        template = "{% load layout_helpers %}" + self.string
        return Template(template).render(self.context)

    def test_dispatches_to_RenderObjectNode(self):
        self.make_str('{% render_model object "$tpl" %}', tpl=self.tpl_name)
        self.assertTrue(self.expected_result in self.rendered_template)

    def test_raises_exception_on_too_many_parameters(self):
        self.make_str('{% render_model object "$tpl" one_too_many %}', tpl=self.tpl_name)
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            self.rendered_template

    def test_raises_exception_on_too_few_parameters(self):
        self.make_str('{% render_model object %}')
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            self.rendered_template

    def test_evaluates_template_as_context_variable(self):
        self.make_str('{% render_model object layout_var %}')
        self.context["layout_var"] = self.tpl_name
        self.assertTrue(self.expected_result in self.rendered_template)

    def test_supports_single_quotes(self):
        self.make_str("{% render_model object '$tpl' %}", tpl=self.tpl_name)
        self.assertTrue(self.expected_result in self.rendered_template)

    def test_raises_exception_on_missing_template(self):
        self.make_str('{% render_model object "missing" %}')
        with self.assertRaises(TemplateDoesNotExist):
            self.rendered_template

    def test_raises_exception_on_missing_context_variable(self):
        self.make_str('{% render_model object layout_var %}')
        with self.assertRaises(VariableDoesNotExist):
            self.rendered_template


class RenderListNodeTestCase(TestCase):
    def test_variable_resolution_for_list(self):
        random_list_name = "list_%d" % random.randint(100, 200)
        rln = RenderListNode(Variable(random_list_name), "'debug'")
        with stub_render_to_string():
            try:
                rln.render(Context({random_list_name: [generate_random_model()]}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_variable_resolution_for_name(self):
        random_name_name = "name_%d" % random.randint(100, 200)
        rln = RenderListNode(Variable('list'), random_name_name)
        with stub_render_to_string():
            try:
                rln.render(Context({'list': [generate_random_model()],
                                    random_name_name: 'debug'}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_finds_new_templates_for_each_model(self):
        rln = RenderListNode(Variable('list'), "'debug'")
        num_models = random.randint(5, 10)
        with stub_render_to_string():
            try:
                rln.render(Context({'list': [generate_random_model()
                    for i in range(num_models)]}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()


class render_listTestCase(TestCase):

    def test_filters_list_argument(self):
        string = """
            {% load layout_helpers %}{% render_list list|slice:":3" "full_page" %}
        """.strip()
        model_list = [generate_random_model()
                        for i in range(random.randint(5, 10))]
        context = Context({"list": model_list})
        rendered = Template(string).render(context)

        self.assertEqual(3, len(re.findall('Full Page', rendered)))
        self.assertTrue(re.search('Title: %s' % model_list[0].title, rendered))
        self.assertTrue(re.search('Title: %s' % model_list[1].title, rendered))
        self.assertTrue(re.search('Title: %s' % model_list[2].title, rendered))
        self.assertFalse(re.search('Title: %s' % model_list[3].title, rendered))


class RenderIterNodeTestCase(TestCase):
    def test_render_empty_block(self):
        node = RenderIterNode(Variable('list'), NodeList())
        rendered = node.render(Context({'list': []}))
        self.assertEqual("", rendered)

    def test_render_non_iterable(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(RenderNextNode("'full_page'"))
        node = RenderIterNode(Variable("list"), nodelist)
        with self.assertRaises(TypeError):
            node.render(Context({"list": model}))

    def test_render_one_element(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(RenderNextNode("'full_page'"))
        node = RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": [model]}))
        self.assertTrue(re.search(model.title, rendered))

    def test_render_multiple_elements(self):
        models = [generate_random_model() for i in range(random.randint(5, 8))]
        nodelist = NodeList()
        nodelist.append(RenderNextNode("'full_page'"))
        nodelist.append(RenderNextNode("'show_request'"))
        nodelist.append(RenderNextNode("'full_page'"))
        node = RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        self.assertFalse(re.search(models[3].title, rendered))

    def test_render_multiple_elements_with_extra_nexts(self):
        models = [generate_random_model() for i in range(2)]
        nodelist = NodeList()
        nodelist.append(RenderNextNode("'full_page'"))
        nodelist.append(RenderNextNode("'full_page'"))
        nodelist.append(RenderNextNode("'show_request'"))
        nodelist.append(RenderNextNode("'show_request'"))
        node = RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertTrue(re.search(models[1].title, rendered))
        self.assertFalse(re.search('request', rendered))

    def test_render_multiple_elements_with_remainder(self):
        models = [generate_random_model() for i in range(random.randint(5, 8))]
        nodelist = NodeList()
        nodelist.append(RenderNextNode("'full_page'"))
        nodelist.append(RenderNextNode("'show_request'"))
        nodelist.append(RenderNextNode("'full_page'"))
        nodelist.append(RenderRemainderNode("'full_page'"))
        node = RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        for model in models[3:]:
            self.assertTrue(re.search(model.title, rendered))
