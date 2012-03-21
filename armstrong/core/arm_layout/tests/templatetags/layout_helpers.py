from django.template import Context, NodeList, RequestContext, Template,\
                            TemplateDoesNotExist, Variable
from django.template.base import VariableDoesNotExist
from django.template.base import TemplateSyntaxError
import re

from .._utils import *
from ...templatetags import layout_helpers


class RenderObjectNodeTestCase(LayoutHelperTestCase):
    def test_dispatches_to_get_layout_template_name(self):
        # TODO: this is a brittle case -- refactor
        model = generate_random_model()
        random_name = '"%d"' % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode("object", random_name)

        fake = Fake()
        fake.is_callable().with_args(model, random_name).expects_call()
        with patched_context(utils.render_model, "get_layout_template_name", 
                fake):
            with stub_render_to_string():
                node.render(Context({"object": model}))

        fudge.verify()

    def test_uses_the_name_provided_to_init_to_lookup_model(self):
        model = generate_random_model()
        random_object_name = "foo_%d" % random.randint(100, 200)
        node = layout_helpers.RenderObjectNode(random_object_name,
                "'full_name'")
        with stub_render_to_string():
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
            with patched_context(backends, "render_to_string",
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
            with patched_context(backends, "render_to_string",
                    render_to_string):
                node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
                result = node.render(context)

    def test_original_context_is_not_contaminated(self):
        model = generate_random_model()
        obj = object()
        context = Context({"object": obj, "list": [model]})
        self.assertEqual(Variable("object").resolve(context), obj,
                msg="sanity check")
        with stub_render_to_string():
            node = layout_helpers.RenderObjectNode("list.0", "'foobar'")
            result = node.render(context)
        self.assertEqual(Variable("object").resolve(context), obj)


class render_modelTestCase(TestCase):
    def setUp(self):
        self.model = generate_random_model()
        self.string = """
            {% load layout_helpers %}{% render_model object "full_page" %}
        """.strip()

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
        self.string += "{% render_model object full_page one_to_many %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too many parameters"
        self.assertEqual(e.exception.message, expected)

    def test_raises_intelligent_exception_on_error_too_few_parameters(self):
        self.string += "{% render_model object %}"
        with self.assertRaises(TemplateSyntaxError) as e:
            self.rendered_template
        expected = "Too few parameters"
        self.assertEqual(e.exception.message, expected)

    def test_evaluates_variable_without_quotations(self):
        self.string += '{% render_model object layout_var %}'
        context = self.context
        context["layout_var"] = "full_page"
        self.assertRegexpMatches(self.template.render(context),
                "Title: %s" % self.model.title)

    def test_supports_single_quotes(self):
        self.string = self.string.replace('"', "'")
        self.assertRegexpMatches(self.rendered_template,
                "Title: %s" % self.model.title)


class RenderListNodeTestCase(LayoutHelperTestCase):
    def test_variable_resolution_for_list(self):
        random_list_name = "list_%d" % random.randint(100, 200)
        rln = layout_helpers.RenderListNode(
                    Variable(random_list_name),
                    "'debug'")
        with stub_render_to_string():
            try:
                rln.render(Context({random_list_name:[generate_random_model()]}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_variable_resolution_for_name(self):
        random_name_name = "name_%d" % random.randint(100, 200)
        rln = layout_helpers.RenderListNode(
                    Variable('list'),
                    random_name_name)
        with stub_render_to_string():
            try:
                rln.render(Context({'list':[generate_random_model()],
                                    random_name_name:'debug'}))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()

    def test_finds_new_templates_for_each_model(self):
        rln = layout_helpers.RenderListNode(
                    Variable('list'),
                    "'debug'")
        num_models = random.randint(5, 10)
        with stub_render_to_string():
            try:
                rln.render(Context({'list':[generate_random_model() for i in
                    range(num_models)] }))
            except VariableDoesNotExist:
                self.fail("should have found variable in context")
        fudge.verify()


class render_listTestCase(NodeParsingTestCase):
    def setUp(self):
        super(NodeParsingTestCase, self).setUp()
        self.string = """
            {% load layout_helpers %}{% render_list list "full_page" %}
        """.strip()
        self.model_list = [generate_random_model()
                    for i in range(random.randint(5, 10))]

    @property
    def context(self):
        return Context({"list": self.model_list})

    def test_filters_list_argument(self):
        self.string = """
            {% load layout_helpers %}{% render_list list|slice:":3" "full_page" %}
        """.strip()
        rendered = self.rendered_template
        self.assertEqual(3, len(re.findall('Full Page', rendered)))
        self.assertTrue(re.search('Title: %s' %
                                self.model_list[0].title, rendered))
        self.assertTrue(re.search('Title: %s' %
                                self.model_list[1].title, rendered))
        self.assertTrue(re.search('Title: %s' %
                                self.model_list[2].title, rendered))
        self.assertFalse(re.search('Title: %s' %
                                self.model_list[3].title, rendered))


class RenderIterNodeTestCase(LayoutHelperTestCase):
    def test_render_empty_block(self):
        node = layout_helpers.RenderIterNode(Variable('list'), NodeList())
        rendered = node.render(Context({'list': []}))
        self.assertEqual("", rendered)

    def test_render_non_iterable(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        with self.assertRaises(TypeError):
            rendered = node.render(Context({"list": model}))

    def test_render_one_element(self):
        model = generate_random_model()
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": [model]}))
        self.assertTrue(re.search(model.title, rendered))

    def test_render_multiple_elements(self):
        models = [generate_random_model() for i in range(random.randint(5,8))]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        self.assertFalse(re.search(models[3].title, rendered))

    def test_render_multiple_elements_with_extra_nexts(self):
        models = [generate_random_model() for i in range(2)]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertTrue(re.search(models[1].title, rendered))
        self.assertFalse(re.search('request', rendered))

    def test_render_multiple_elements_with_remainder(self):
        models = [generate_random_model() for i in range(random.randint(5,8))]
        nodelist = NodeList()
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderNextNode("'show_request'"))
        nodelist.append(layout_helpers.RenderNextNode("'full_page'"))
        nodelist.append(layout_helpers.RenderRemainderNode("'full_page'"))
        node = layout_helpers.RenderIterNode(Variable("list"), nodelist)
        rendered = node.render(Context({"list": models}))
        self.assertTrue(re.search(models[0].title, rendered))
        self.assertFalse(re.search(models[1].title, rendered))
        self.assertTrue(re.search(models[2].title, rendered))
        for model in models[3:]:
            self.assertTrue(re.search(model.title, rendered))

