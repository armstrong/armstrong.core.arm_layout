from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


def get_layout_template_name(model, name):
    ret = []
    for a in model.__class__.mro():
        if not hasattr(a, "_meta"):
            continue
        ret.append("layout/%s/%s/%s.html" % (a._meta.app_label,
            a._meta.object_name.lower(), name))
    return ret


def render_model(object, name, dictionary=None, context_instance=None):
    dictionary = dictionary or {}
    dictionary["object"] = object
    return mark_safe(render_to_string(get_layout_template_name(object, name),
        dictionary=dictionary, context_instance=context_instance))
