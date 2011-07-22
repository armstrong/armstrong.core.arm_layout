from .arm_layout_support.models import SubFoobar
from ._utils import *
from ..utils import get_layout_template_name


class get_layout_template_nameTestCase(LayoutHelperTestCase):
    def test_uses_model_name_in_template_name(self):
        random_model_name = "model_name_%d" % random.randint(100, 200)
        model = generate_random_model()
        model._meta.object_name = random_model_name
        result = get_layout_template_name(model, "full_name")
        expected = ["layout/arm_layout_support/%s/full_name.html" % (
                random_model_name
        )]
        self.assertEqual(result, expected)

    def test_uses_app_label_in_template_name(self):
        random_app_label = "app_label_%d" % random.randint(100, 200)
        model = generate_random_model()
        model._meta.app_label = random_app_label
        result = get_layout_template_name(model, "full_name")
        expected = ["layout/%s/foobar/full_name.html" % random_app_label]
        self.assertEqual(result, expected)

    def test_uses_name_in_template_name(self):
        random_name = "layout_name_%d" % random.randint(100, 200)
        model = generate_random_model()
        result = get_layout_template_name(model, random_name)
        expected = ["layout/arm_layout_support/foobar/%s.html" % random_name]
        self.assertEqual(result, expected)

    def test_can_find_templates_through_models_inheritance(self):
        sub = SubFoobar()
        result = get_layout_template_name(sub, "full_name")
        expected = ["layout/arm_layout_support/subfoobar/full_name.html",
                "layout/arm_layout_support/foobar/full_name.html",
        ]
        self.assertEqual(result, expected)
