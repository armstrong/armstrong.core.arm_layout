import abc
import random
import fudge
from contextlib import contextmanager

from ..arm_layout_support.models import *


class BackendTestCaseMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def backend_class(self):
        """backend_class = TestThisBackend"""

    def __init__(self, *args, **kwargs):
        super(BackendTestCaseMixin, self).__init__(*args, **kwargs)
        self.backend = self.backend_class()
        self.name = "full_page"
        basemodel = Foobar()
        self.root_model_path = 'layout/%s/%s/' % (
            basemodel._meta.app_label,
            basemodel._meta.object_name.lower())

    @staticmethod
    @contextmanager
    def model_meta_randomizer(model, attr):
        original = getattr(model._meta, attr)
        value = "random_%d" % random.randint(100, 200)
        setattr(model._meta, attr, value)
        yield value
        setattr(model._meta, attr, original)

    def test_requires_a_model_instance(self):
        with self.assertRaises(TypeError):
            self.backend.get_layout_template_name(Foobar, self.name)

    def test_returns_proper_path(self):
        expected = ['%s%s.html' % (self.root_model_path, self.name)]
        result = self.backend.get_layout_template_name(Foobar(), self.name)
        self.assertEqual(expected, result)

    def test_renderer_can_specify_base_path(self):
        model = Foobar()
        with fudge.patched_context(self.backend, "base_layout_directory", "different"):
            result = self.backend.get_layout_template_name(model, self.name)

        expected = ['different/%s/%s/%s.html' % (
            model._meta.app_label, model._meta.object_name.lower(), self.name)]
        self.assertEqual(expected, result)

    def test_missing_file_is_okay(self):
        model = Foobar()
        file_doesnt_exist = "fake_template"
        expected = ['layout/%s/%s/%s.html' % (
            model._meta.app_label,
            model._meta.object_name.lower(),
            file_doesnt_exist)]

        result = self.backend.get_layout_template_name(model, file_doesnt_exist)
        self.assertEqual(expected, result)

    def test_uses_app_label_in_template_name(self):
        model = Foobar()

        with self.model_meta_randomizer(model, 'app_label') as app_label:
            expected = ['layout/%s/%s/%s.html' % (
                app_label, model._meta.object_name.lower(), self.name)]
            result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)

    def test_uses_model_name_in_template_name(self):
        model = Foobar()

        with self.model_meta_randomizer(model, 'object_name') as object_name:
            expected = ['layout/%s/%s/%s.html' % (
                model._meta.app_label, object_name, self.name)]
            result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)

    def test_uses_name_in_template_name(self):
        name = "random_%d" % random.randint(100, 200)
        expected = ['%s%s.html' % (self.root_model_path, name)]

        result = self.backend.get_layout_template_name(Foobar(), name)
        self.assertEqual(expected, result)

    def test_proper_model_inheritance_order(self):
        model = SubFoobar()

        model_path = 'layout/%s/%s/' % \
            (model._meta.app_label, model._meta.object_name.lower())
        expected = [
            '%s%s.html' % (model_path, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)

    def test_abstract_models_are_used(self):
        concrete = ConcreteFoo()
        abstract = AbstractFoo()

        concrete_path = 'layout/%s/%s/' % \
            (concrete._meta.app_label, concrete._meta.object_name.lower())
        abstract_path = 'layout/%s/%s/' % \
            (abstract._meta.app_label, abstract._meta.object_name.lower())
        expected = [
            '%s%s.html' % (concrete_path, self.name),
            '%s%s.html' % (abstract_path, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(concrete, self.name)
        self.assertEqual(expected, result)

    def test_proxy_models_are_used(self):
        model = ProxyFoo()

        model_path = 'layout/%s/%s/' % \
            (model._meta.app_label, model._meta.object_name.lower())
        expected = [
            '%s%s.html' % (model_path, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)
