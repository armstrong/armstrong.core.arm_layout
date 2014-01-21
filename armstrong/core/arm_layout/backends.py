from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class BasicLayoutBackend(object):
    def get_layout_template_name(self, model, name):
        ret = []
        for a in model.__class__.mro():
            if not hasattr(a, "_meta"):
                continue
            ret.append("layout/%s/%s/%s.html" % (a._meta.app_label,
                a._meta.object_name.lower(), name))
        return ret

    def render(self, object, name, dictionary=None, context_instance=None):
        dictionary = dictionary or {}
        dictionary["object"] = object
        template_name = self.get_layout_template_name(object, name)
        return mark_safe(render_to_string(template_name, dictionary=dictionary,
            context_instance=context_instance))

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)


# DEPRECATED: To be removed in ArmLayout 2.0
import warnings


def deprecate(cls):
    def wrapper(*args, **kwargs):
        msg = "BasicRenderModelBackend is deprecated and will be removed in ArmLayout 2.0. Use %s."
        warnings.warn(msg % cls.__name__, DeprecationWarning)
        return cls(*args, **kwargs)
    return wrapper

BasicRenderModelBackend = deprecate(BasicLayoutBackend)
