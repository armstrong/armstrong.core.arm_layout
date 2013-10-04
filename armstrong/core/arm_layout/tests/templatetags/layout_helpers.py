import random
import fudge
from django.conf import settings
from django.test import signals
from django.template import (Context, Template,
    TemplateDoesNotExist, TemplateSyntaxError)

from ..arm_layout_support.models import Foobar
from .._utils import TestCase


def generate_random_models(count):
    """Generator to create ``count`` number of unique random models"""

    num = random.randint(1000, 2000)
    while count > 0:
        yield Foobar(title="This is a random title %d" % num)
        num += random.randint(2, 20)
        count -= 1


class RenderBaseTestCaseMixin(object):
    def setUp(self):
        self.string = ""
        self.context = Context()

    def tearDown(self):
        # cache the rendered template result during a test run
        if hasattr(self, '_rendered_template'):
            del self._rendered_template

    @classmethod
    def setUpClass(cls):
        """Set Template settings to known values"""
        cls.old_td, settings.TEMPLATE_DEBUG = settings.TEMPLATE_DEBUG, False
        cls.old_invalid, settings.TEMPLATE_STRING_IF_INVALID = settings.TEMPLATE_STRING_IF_INVALID, 'INVALID'

    @classmethod
    def tearDownClass(cls):
        settings.TEMPLATE_DEBUG = cls.old_td
        settings.TEMPLATE_STRING_IF_INVALID = cls.old_invalid


class RenderModelTestCase(RenderBaseTestCaseMixin, TestCase):
    def setUp(self):
        super(RenderModelTestCase, self).setUp()
        self.model = next(generate_random_models(1))
        self.context['model_obj'] = self.model
        self.expected_result = "Full - Title: %s" % self.model.title

    @property
    def rendered_template(self):
        if not hasattr(self, '_rendered_template'):
            template = "{% load layout_helpers %}" + self.string
            self._rendered_template = Template(template).render(self.context)
        return self._rendered_template

    def test_renders_object(self):
        self.string = '{% render_model model_obj "full" %}'
        self.assertEqual(self.expected_result, self.rendered_template)

    def test_raises_exception_on_too_many_parameters(self):
        self.string = '{% render_model model_obj "full" one_too_many %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            self.rendered_template

    def test_raises_exception_on_too_few_parameters(self):
        self.string = '{% render_model model_obj %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            self.rendered_template

    def test_variable_resolution_for_template(self):
        self.string = '{% render_model model_obj layout_var %}'
        self.context["layout_var"] = "full"
        self.assertEqual(self.expected_result, self.rendered_template)

    def test_raises_exception_on_missing_template(self):
        self.string = '{% render_model model_obj "missing" %}'
        with self.assertRaises(TemplateDoesNotExist):
            self.rendered_template

    @fudge.patch(
        'armstrong.core.arm_layout.utils.render_model.get_layout_template_name',
        'armstrong.core.arm_layout.backends.render_to_string')
    def test_dispatches_to_get_layout_template_name(self, fake_get_layout, fake_render):
        fake_get_layout.expects_call().with_args(self.model, 'tpl')
        fake_render.is_callable().returns("")  # prevent actual template file loading

        self.string = '{% render_model model_obj "tpl" %}'
        self.rendered_template

    def test_can_pull_object_out_of_complex_context(self):
        self.context = Context(dict(list=[self.model]))
        self.string = '{% render_model list.0 "full" %}'
        self.assertEqual(self.expected_result, self.rendered_template)

    def test_rendered_context_sets_provided_obj_as_object_variable(self):
        # Copying the capture technique used by django.test.client.request()
        def on_template_render(signal, sender, template, context, **kwargs):
            if template.name.endswith('full.html'):
                self.assertTrue('object' in context)
                self.assertEqual(self.model, context['object'])
        signals.template_rendered.connect(on_template_render, dispatch_uid="template-render")

        self.string = '{% render_model model_obj "full" %}'
        try:
            self.assertEqual(self.expected_result, self.rendered_template)
        finally:
            signals.template_rendered.disconnect(dispatch_uid="template-render")

    def test_original_context_is_not_contaminated(self):
        obj = fudge.Fake().expects_call().returns("object output!")
        self.context['object'] = obj
        self.string = '{% render_model model_obj "full" %} {{ object }}'
        self.expected_result += ' object output!'

        # Copying the capture technique used by django.test.client.request()
        def on_template_render(signal, sender, template, context, **kwargs):
            if not template.name.endswith('full.html'):
                self.assertEqual(obj, context['object'])
        signals.template_rendered.connect(on_template_render, dispatch_uid="template-render")

        try:
            self.assertEqual(self.expected_result, self.rendered_template)
        finally:
            signals.template_rendered.disconnect(dispatch_uid="template-render")

        fudge.verify()

    def test_filters_work_on_obj_argument(self):
        self.string = '{% render_model model_obj|default:"nothing" "full" %}'
        self.assertEqual(self.expected_result, self.rendered_template)

    def test_filters_work_on_template_argument(self):
        self.string = '{% render_model model_obj "full_extra"|slice:":4" %}'
        self.assertEqual(self.expected_result, self.rendered_template)


class RenderListTestCase(RenderBaseTestCaseMixin, TestCase):
    @property
    def rendered_template(self):
        if not hasattr(self, '_rendered_template'):
            template = "{% load layout_helpers %}" + self.string
            self._rendered_template = Template(template).render(self.context)
        return self._rendered_template

    def test_render_empty_list(self):
        self.assertEqual(self.rendered_template, "")

    def test_render_raises_exception_on_non_iterable(self):
        self.context['list'] = None
        self.string = '{% render_list list "full" %}'
        with self.assertRaises(TypeError):
            self.rendered_template

    def test_raises_exception_on_too_many_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_list list "full" one_too_many %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            self.rendered_template

    def test_raises_exception_on_too_few_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_list list %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            self.rendered_template

    def test_renders_all_list_items(self):
        models = list(generate_random_models(3))

        self.context['list'] = models
        self.string = '{% render_list list "full" %}'

        self.assertEqual(self.rendered_template.count('Full - Title'), 3)
        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertTrue(models[2].title in self.rendered_template)

    def test_variable_resolution_for_list(self):
        random_list_var = "var_%d" % random.randint(100, 200)
        models = list(generate_random_models(2))

        self.context[random_list_var] = models
        self.string = '{% render_list ' + random_list_var + ' "full" %}'

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)

    def test_variable_resolution_for_template(self):
        random_tpl_var = "name_%d" % random.randint(100, 200)

        self.context['list'] = list(generate_random_models(2))
        self.string = '{% render_list list "' + random_tpl_var + '" %}'

        with self.assertRaisesRegexp(TemplateDoesNotExist, "%s.html" % random_tpl_var):
            self.rendered_template

    def test_filters_work_on_list_argument(self):
        models = list(generate_random_models(5))

        self.context['list'] = models
        self.string = '{% render_list list|slice:":2" "full" %}'

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertFalse(models[2].title in self.rendered_template)

    def test_filters_work_on_template_argument(self):
        models = list(generate_random_models(2))

        self.context['list'] = models
        self.string = '{% render_list list "full_extra"|slice:":4" %}'

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)


class RenderIterTestCase(RenderBaseTestCaseMixin, TestCase):
    def setUp(self):
        super(RenderIterTestCase, self).setUp()
        self.variable_name = 'list'

    @property
    def rendered_template(self):
        if not hasattr(self, '_rendered_template'):
            template = ''.join([
                "{% load layout_helpers %}",
                "{% render_iter " + self.variable_name + " %}",
                self.string,
                '{% endrender_iter %}'])
            self._rendered_template = Template(template).render(self.context)
        return self._rendered_template

    def test_iter_raises_exception_on_too_many_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        template = '{% load layout_helpers %}{% render_iter list one_too_many %}{% endrender_iter %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            Template(template).render(self.context)

    def test_iter_raises_exception_on_too_few_parameters(self):
        template = '{% load layout_helpers %}{% render_iter %}{% endrender_iter %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            Template(template).render(self.context)

    def test_next_raises_exception_on_too_many_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_next "mini" one_too_many %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            self.rendered_template

    def test_next_raises_exception_on_too_few_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_next %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            self.rendered_template

    def test_remainder_raises_exception_on_too_many_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_remainder "mini" one_too_many %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too many parameters"):
            self.rendered_template

    def test_remainder_raises_exception_on_too_few_parameters(self):
        self.context['list'] = list(generate_random_models(1))
        self.string = '{% render_remainder %}'
        with self.assertRaisesRegexp(TemplateSyntaxError, "Too few parameters"):
            self.rendered_template

    def test_render_empty_block(self):
        self.assertEqual(self.rendered_template, "")

    def test_render_raises_exception_on_non_iterable(self):
        self.context['list'] = None
        self.string = '{% render_next "full" %}'
        with self.assertRaises(TypeError):
            self.rendered_template

    def test_render_one_element(self):
        model = next(generate_random_models(1))
        self.context['list'] = [model]
        self.string = '{% render_next "full" %}'
        self.assertEqual('Full - Title: %s' % model.title, self.rendered_template)

    def test_render_multiple_elements(self):
        models = list(generate_random_models(5))

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
        models = list(generate_random_models(7))

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

    def test_render_empty_list_ignores_extras(self):
        self.context['list'] = []
        self.string = ''.join([
            '{% render_next "full" %}',
            '{% render_remainder "mini" %}'])
        self.assertEqual(self.rendered_template, "")

    def test_render_ignores_extras(self):
        models = list(generate_random_models(2))

        self.context['list'] = models
        self.string = ''.join([
            '{% render_next "full" %}',
            '{% render_next "full" %}',
            '{% render_next "mini" %}',
            '{% render_remainder "mini" %}'])

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue(models[1].title in self.rendered_template)
        self.assertFalse('mini' in self.rendered_template)

    def test_iter_variable_resolution_for_list(self):
        models = list(generate_random_models(1))

        self.variable_name = "var_%d" % random.randint(100, 200)
        self.context[self.variable_name] = models
        self.string = '{% render_next "full" %}'

        self.assertTrue(models[0].title in self.rendered_template)

    def test_next_variable_resolution_for_template(self):
        random_tpl_var = "name_%d" % random.randint(100, 200)

        self.context['list'] = list(generate_random_models(2))
        self.string = '{% render_next "' + random_tpl_var + '" %}'

        with self.assertRaisesRegexp(TemplateDoesNotExist, "%s.html" % random_tpl_var):
            self.rendered_template

    def test_remainder_variable_resolution_for_template(self):
        random_tpl_var = "name_%d" % random.randint(100, 200)

        self.context['list'] = list(generate_random_models(2))
        self.string = '{% render_remainder "' + random_tpl_var + '" %}'

        with self.assertRaisesRegexp(TemplateDoesNotExist, "%s.html" % random_tpl_var):
            self.rendered_template

    def test_filters_work_on_list_argument(self):
        models = list(generate_random_models(2))

        self.context['list'] = models
        self.string = '{% render_remainder "full" %}'

        self.variable_name = 'list|slice:":1"'
        self.assertTrue(models[0].title in self.rendered_template)
        self.assertFalse(models[1].title in self.rendered_template)

    def test_filters_work_on_template_argument(self):
        models = list(generate_random_models(2))

        self.context['list'] = models
        self.string = ''.join([
            '{% render_next "full_extra"|slice:":4" %}',
            '{% render_remainder "mini_extra"|slice:":4" %}'])

        self.assertTrue(models[0].title in self.rendered_template)
        self.assertTrue('mini' in self.rendered_template)
