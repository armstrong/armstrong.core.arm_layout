from django.db import models
from armstrong.core.arm_layout.mixins import *


class Foobar(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        app_label = "support"


class SubFoobar(Foobar):
    class Meta:
        app_label = "support"


class AbstractFoo(Foobar):
    class Meta:
        abstract = True
        app_label = "support"


class ConcreteFoo(AbstractFoo):
    class Meta:
        app_label = "support"


class ProxyFoo(Foobar):
    class Meta:
        proxy = True
        app_label = "support"


class HasOwnLayoutMethod(models.Model):
    def get_layout_template_name(self, name):
        return ["my_layouts/%s/%s.file" % (type(self).__name__.lower(), name)]

    class Meta:
        app_label = "support"


class Base(models.Model):  # so we can test inheritance
    class Meta:
        app_label = "support"


class TemplatesBySlugModel(TemplatesBySlugMixin, Base):
    slug = models.SlugField()

    class Meta:
        app_label = "support"


class TemplatesByFullSlugModel(TemplatesByFullSlugMixin, Base):
    full_slug = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = "support"


class TypeWithSlugModel(Base):
    slug = models.SlugField()

    class Meta:
        app_label = "support"


class TemplatesByTypeModel(TemplatesByTypeMixin, Base):
    type = models.ForeignKey(TypeWithSlugModel)

    class Meta:
        app_label = "support"
