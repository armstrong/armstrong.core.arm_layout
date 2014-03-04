from django.db import models
from armstrong.core.arm_layout.mixins import *


class Foobar(models.Model):
    title = models.CharField(max_length=100)


class SubFoobar(Foobar):
    pass


class AbstractFoo(Foobar):
    class Meta:
        abstract = True


class ConcreteFoo(AbstractFoo):
    pass


class ProxyFoo(Foobar):
    class Meta:
        proxy = True


class HasOwnLayoutMethod(models.Model):
    def get_layout_template_name(self, name):
        return ["my_layouts/%s/%s.file" % (type(self).__name__.lower(), name)]


class Base(models.Model):
    pass  # so we can test inheritance


class TemplatesBySlugModel(TemplatesBySlugMixin, Base):
    slug = models.SlugField()


class TemplatesByFullSlugModel(TemplatesByFullSlugMixin, Base):
    full_slug = models.CharField(max_length=255, blank=True)


class TypeWithSlugModel(Base):
    slug = models.SlugField()


class TemplatesByTypeModel(TemplatesByTypeMixin, Base):
    type = models.ForeignKey(TypeWithSlugModel)
