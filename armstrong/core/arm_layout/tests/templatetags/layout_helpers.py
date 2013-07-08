import re
import string
import random
import fudge
from fudge.inspector import arg
from contextlib import contextmanager

from django.template import (
    Template, Context, NodeList, Variable,
    TemplateDoesNotExist, TemplateSyntaxError, VariableDoesNotExist)

from ..arm_layout_support.models import Foobar
from ...templatetags.layout_helpers import (
    RenderObjectNode, RenderListNode, RenderIterNode,
    RenderNextNode, RenderRemainderNode)
from ... import utils, backends
from .._utils import TestCase


def generate_random_model():
    random_title = "This is a random title %d" % random.randint(1000, 2000)
    return Foobar(title=random_title)


@contextmanager
def stub_render_to_string():
    render_to_string = fudge.Fake().is_callable().returns("")
    with fudge.patched_context(backends, "render_to_string",
            render_to_string):
        yield


@contextmanager
def stub_get_layout_template_name():
    get_layout_template_name = fudge.Fake().is_callable().returns("")
    with fudge.patched_context(utils.render_model, "get_layout_template_name",
            get_layout_template_name):
        yield


class RenderBaseTestCaseMixin(object):
    def setUp(self):
        self.string = ""
        self.context = Context()

    def tearDown(self):
        # cache the rendered template result during a test run
        if hasattr(self, '_rendered_template'):
            del self._rendered_template



class RenderObjectNodeTestCase(RenderBaseTestCaseMixin, TestCase):
    def setUp(self):
        super(RenderObjectNodeTestCase, self).setUp()
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
        with fudge.patched_context(utils.render_model,
                "get_layout_template_name", fake):
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

    def test_object_is_provided_to_context(self):
        context = Context({"object": self.model})

        with stub_get_layout_template_name():
            render_to_string = fudge.Fake().is_callable().expects_call()
            node = RenderObjectNode("object", "'foobar'")
            render_to_string.with_args(
                arg.any(),
                dictionary=self.contains_model(self.model),
                context_instance=context)
            with fudge.patched_context(backends, "render_to_string",
                    render_to_string):
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
            with fudge.patched_context(backends, "render_to_string",
                    render_to_string):
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


class render_modelTestCase(RenderBaseTestCaseMixin, TestCase):
    def setUp(self):
        self.model = generate_random_model()
        self.string = ""
        self.tpl_name = "full"
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


class RenderListTestCase(RenderBaseTestCaseMixin, TestCase):
    @property
    def rendered_template(self):
        if not hasattr(self, '_rendered_template'):
            template = "{% load layout_helpers %}" + self.string
            self._rendered_template = Template(template).render(self.context)
        return self._rendered_template

    def test_renders_all_list_items(self):
        models = [generate_random_model() for i in range(3)]

        self.context['list'] = models
        self.string = '{% render_list list "full" %}'

        self.assertEqual(self.rendered_template.count('Full - Title'), 3)
        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertTrue(models[2].title in self.rendered_template)

    def test_variable_resolution_for_list(self):
        random_list_var = "var_%d" % random.randint(100, 200)
        models = [generate_random_model() for i in range(2)]

        self.context[random_list_var] = models
        self.string = '{% render_list ' + random_list_var + ' "full" %}'

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)

    def test_variable_resolution_for_template(self):
        random_tpl_var = "name_%d" % random.randint(100, 200)

        self.context['list'] = [generate_random_model() for i in range(2)]
        self.string = '{% render_list list "' + random_tpl_var + '" %}'

        with self.assertRaisesRegexp(TemplateDoesNotExist, "%s.html" % random_tpl_var):
            self.rendered_template

    def test_filters_list_argument(self):
        models = [generate_random_model() for i in range(5)]

        self.context['list'] = models
        self.string = '{% render_list list|slice:":2" "full" %}'

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertFalse(models[2].title in self.rendered_template)


class RenderIterTestCase(RenderBaseTestCaseMixin, TestCase):
    @property
    def rendered_template(self):
        if not hasattr(self, '_rendered_template'):
            template = ''.join([
                "{% load layout_helpers %}",
                "{% render_iter list %}",
                self.string,
                '{% endrender_iter %}'])
            self._rendered_template = Template(template).render(self.context)
        return self._rendered_template

    def test_render_empty_block(self):
        self.assertEqual(self.rendered_template, "")

    def test_render_raises_exception_on_non_iterable(self):
        self.context['list'] = None
        self.string = '{% render_next "full" %}'
        with self.assertRaises(TypeError):
            self.rendered_template

    def test_render_one_element(self):
        model = generate_random_model()
        self.context['list'] = [model]
        self.string = '{% render_next "full" %}'
        self.assertEqual('Full - Title: %s' % model.title, self.rendered_template)

    def test_render_multiple_elements(self):
        models = [generate_random_model() for i in range(5)]

        self.context['list'] = models
        self.string = ''.join([
            '{% render_next "full" %}',
            '{% render_next "mini" %}',
            '{% render_next "full" %}'])

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertFalse(models[1].title in self.rendered_template)
        self.assertTrue(models[2].title in self.rendered_template)
        self.assertFalse(models[3].title in self.rendered_template)

    def test_render_multiple_elements_with_remainder(self):
        models = [generate_random_model() for i in range(7)]

        self.context['list'] = models
        self.string = ''.join([
            '{% render_next "full" %}',
            '{% render_next "mini" %}',
            '{% render_next "full" %}',
            '{% render_remainder "full" %}'])

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertFalse(models[1].title in self.rendered_template)
        self.assertTrue(models[2].title in self.rendered_template)
        for model in models[3:]:
            self.assertTrue(model.title in self.rendered_template)

    def test_render_ignores_extras(self):
        models = [generate_random_model() for i in range(2)]

        self.context['list'] = models
        self.string = ''.join([
            '{% render_next "full" %}',
            '{% render_next "full" %}',
            '{% render_next "mini" %}',
            '{% render_remainder "mini" %}'])

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertFalse('mini' in self.rendered_template)
