from ...backends import ModelProvidedLayoutBackend
from ..arm_layout_support.models import HasOwnLayoutMethod
from .._utils import TestCase
from ._common import BackendTestCaseMixin


class ModelProvidedLayoutBackendTestCase(BackendTestCaseMixin, TestCase):
    backend_class = ModelProvidedLayoutBackend

    def test_returns_model_provided_templates(self):
        model = HasOwnLayoutMethod()
        result = self.backend.get_layout_template_name(model, self.name)
        expected = 'my_layouts/%s/%s.file' % \
            (model._meta.object_name.lower(), self.name)
        self.assertEqual([expected], result)
