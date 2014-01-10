import abc
import random
import fudge

from ..arm_layout_support.models import Foobar, SubFoobar


class BackendTestCaseMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def backend_class(self):
        """backend_class = TestThisBackend"""

    def __init__(self, *args, **kwargs):
        super(BackendTestCaseMixin, self).__init__(*args, **kwargs)
        self.backend = self.backend_class()

    def setUp(self):
        super(BackendTestCaseMixin, self).setUp()
        self.m = Foobar()
        self.m2 = SubFoobar()
        self.name = "full_page"
        self._original_object_name = self.m._meta.object_name
        self._original_app_label = self.m._meta.app_label

    def tearDown(self):
        self.m._meta.object_name = self._original_object_name
        self.m._meta.app_label = self._original_app_label
        super(BackendTestCaseMixin, self).tearDown()

    def test_requires_a_model_instance(self):
        with self.assertRaises(TypeError):
            self.backend.get_layout_template_name(type(self.m), self.name)

    def test_returns_proper_path(self):
        result = self.backend.get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.object_name.lower(),
             self.name)
        self.assertEqual([expected], result)

    def test_renderer_can_specify_base_path(self):
        with fudge.patched_context(self.backend, "base_layout_directory", "different"):
            result = self.backend.get_layout_template_name(self.m, self.name)

        expected = 'different/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.object_name.lower(),
             self.name)
        self.assertEqual([expected], result)

    def test_missing_file_is_okay(self):
        file_doesnt_exist = "fake_template"
        result = self.backend.get_layout_template_name(self.m, file_doesnt_exist)
        expected = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label,
             self.m._meta.object_name.lower(),
             file_doesnt_exist)
        self.assertEqual([expected], result)

    def test_uses_app_label_in_template_name(self):
        self.m._meta.app_label = "random_%d" % random.randint(100, 200)
        result = self.backend.get_layout_template_name(self.m, self.name)
        expected = 'layout/%s/foobar/%s.html' % \
            (self.m._meta.app_label, self.name)
        self.assertEqual([expected], result)

    def test_uses_model_name_in_template_name(self):
        self.m._meta.object_name = "random_%d" % random.randint(100, 200)
        result = self.backend.get_layout_template_name(self.m, self.name)
        expected = 'layout/arm_layout_support/%s/%s.html' % \
            (self.m._meta.object_name, self.name)
        self.assertEqual([expected], result)

    def test_uses_name_in_template_name(self):
        name = "random_%d" % random.randint(100, 200)
        result = self.backend.get_layout_template_name(self.m, name)
        expected = 'layout/arm_layout_support/foobar/%s.html' % name
        self.assertEqual([expected], result)

    def test_proper_model_inheritance_order(self):
        result = self.backend.get_layout_template_name(self.m2, self.name)
        expected_child = 'layout/%s/%s/%s.html' % \
            (self.m2._meta.app_label, self.m2._meta.object_name.lower(), self.name)
        expected_parent = 'layout/%s/%s/%s.html' % \
            (self.m._meta.app_label, self.m._meta.object_name.lower(), self.name)

        self.assertEqual([expected_child, expected_parent], result)
