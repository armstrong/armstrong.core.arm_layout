class ModelPathBaseMixin(object):
    base_layout_directory = "layout"

    def _build_model_path(self, model_obj):
        return "%s/%s/%s/" % (
            self.base_layout_directory,
            model_obj._meta.app_label,
            model_obj._meta.object_name.lower())


class TemplatesBySlugMixin(ModelPathBaseMixin):
    """
    Look up model templates by slug.

    Designed for use with the ModelProvidedLayoutBackend.
    Use this mixin on a model with a `slug` field.
    It follows the normal model inheritance lookup structure, but
    for each model looks first in a folder named after the slug.
    ex: "child_model/slug/template.html"
        "child_model/template.html"
        "parent_model/slug/template.html"
        "parent_model/template.html"

    """
    def get_layout_template_name(self, name):
        tpls = []

        for a in self.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            base_path = self._build_model_path(a)
            tpls.extend([
                "%s%s/%s.html" % (base_path, self.slug, name),
                "%s%s.html" % (base_path, name)])
        return tpls


class TemplatesByFullSlugMixin(ModelPathBaseMixin):
    """
    Look up model templates using the full_slug as directory structure.

    Designed for use with the ModelProvidedLayoutBackend.
    Use this mixin on a model with a `full_slug` field that
    demarcates each section with a forward slash. Each section
    of the full_slug is treated as a directory.
    ex: "child_model/slug/more/specific/template.html"
        "child_model/slug/more/template.html"
        "child_model/slug/template.html"
        "child_model/template.html"
        "parent_model/slug/more/specific/template.html"
        "parent_model/slug/more/template.html"
        "parent_model/slug/template.html"
        "parent_model/template.html"

    """
    def get_layout_template_name(self, name):
        tpls = []

        for a in self.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            base_path = self._build_model_path(a)

            full_slug = self.full_slug
            i = full_slug.rfind("/")
            while i > 0:
                full_slug = full_slug[0:i]  # drop slash and any child slug
                tpls.append("%s%s/%s.html" % (base_path, full_slug, name))
                i = full_slug.rfind("/")

            tpls.append("%s%s.html" % (base_path, name))
        return tpls


class TemplatesByTypeMixin(ModelPathBaseMixin):
    """
    Look up templates by the model instance type.

    Designed for use with the ModelProvidedLayoutBackend.
    Use this mixin on a model with a `type` field where the "type" model
    has a `slug` field. Useful in cases where you want a shared look for
    all instances of a type. Because we only care about this categorization
    of instances, only look for a type/slug combination. We don't actually
    care about the "type" model. Fallback to the normal model path lookup.
    ex: "child_type_model/slug/template.html"
        "parent_type_model/slug/template.html"
        "child_model/template.html"
        "parent_model/template.html"
    It will not include "type_model/template.html".

    """
    def get_layout_template_name(self, name):
        tpls = []

        # build the path for the type model using the slug
        for a in self.type.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            type_path = self._build_model_path(a)
            tpls.append("%s%s/%s.html" % (type_path, self.type.slug, name))

        # build the normal model path
        for a in self.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            base_path = self._build_model_path(a)
            tpls.append("%s%s.html" % (base_path, name))
        return tpls
