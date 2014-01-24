from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from ..mixins import ModelPathBaseMixin


class BasicLayoutBackend(ModelPathBaseMixin):
    """
    Look up model templates using model inheritance as a directory structure.

    This is the default backend. Template lookup follows a directory
    structure based on class inheritance, children first then parents,
    and only considers actual Django model classes. Abstract and proxy
    models also work.

    ex: "proxy_model/template.html"
        "child_model/template.html"
        "parent_model/template.html"

    """
    def get_layout_template_name(self, model_obj, name):
        ret = []
        for a in model_obj.__class__.mro():
            if not hasattr(a, "_meta"):
                continue
            base_path = self._build_model_path(a)
            ret.append("%s%s.html" % (base_path, name))
        return ret

    def render(self, object, name, dictionary=None, context_instance=None):
        dictionary = dictionary or {}
        dictionary["object"] = object
        template_names = self.get_layout_template_name(object, name)
        return mark_safe(render_to_string(
            template_names,
            dictionary=dictionary,
            context_instance=context_instance))

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)
