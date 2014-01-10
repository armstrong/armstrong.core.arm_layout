from ..backends import ModelProvidedLayoutBackend
from .arm_layout_support.models import *
from ._utils import TestCase


class ModelMixinBaseTestCase(TestCase):
    backend = ModelProvidedLayoutBackend()

    def setUp(self):
        super(ModelMixinBaseTestCase, self).setUp()
        self.name = "full_page"
        basemodel = Base()
        self.root_model_path = 'layout/%s/%s/' % (
            basemodel._meta.app_label,
            basemodel._meta.object_name.lower())


class TemplatesBySlugTestCase(ModelMixinBaseTestCase):
    def test_returns_proper_path(self):
        model = TemplatesBySlugModel(slug="haveaslug")

        base_path = 'layout/%s/%s/' % \
            (model._meta.app_label, model._meta.object_name.lower())
        expected = [
            '%s%s/%s.html' % (base_path, model.slug, self.name),
            '%s%s.html' % (base_path, self.name),
            '%s%s/%s.html' % (self.root_model_path, model.slug, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)


class TemplatesByFullSlugTestCase(ModelMixinBaseTestCase):
    def test_returns_proper_path(self):
        model = TemplatesByFullSlugModel(full_slug="have/a/slug/")

        base_path = 'layout/%s/%s/' % \
            (model._meta.app_label, model._meta.object_name.lower())
        expected = [
            '%shave/a/slug/%s.html' % (base_path, self.name),
            '%shave/a/%s.html' % (base_path, self.name),
            '%shave/%s.html' % (base_path, self.name),
            '%s%s.html' % (base_path, self.name),
            '%shave/a/slug/%s.html' % (self.root_model_path, self.name),
            '%shave/a/%s.html' % (self.root_model_path, self.name),
            '%shave/%s.html' % (self.root_model_path, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)


class TemplatesByTypeTestCase(ModelMixinBaseTestCase):
    def test_returns_proper_path(self):
        typeobj = TypeWithSlugModel(slug="editorspicks")
        model = TemplatesByTypeModel(type=typeobj)

        type_base = 'layout/%s/%s/' % \
            (typeobj._meta.app_label, typeobj._meta.object_name.lower())
        model_path = 'layout/%s/%s/' % \
            (model._meta.app_label, model._meta.object_name.lower())
        expected = [
            '%s%s/%s.html' % (type_base, typeobj.slug, self.name),
            '%s%s/%s.html' % (self.root_model_path, typeobj.slug, self.name),
            '%s%s.html' % (model_path, self.name),
            '%s%s.html' % (self.root_model_path, self.name)]

        result = self.backend.get_layout_template_name(model, self.name)
        self.assertEqual(expected, result)
