from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from armstrong.utils.backends import GenericBackend


template_finder = GenericBackend('ARMSTRONG_LAYOUT_TEMPLATE_FINDER',
        defaults='armstrong.core.arm_layout.utils.get_layout_template_name')\
        .get_backend


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
    return mark_safe(render_to_string(template_finder(object, name),
        dictionary=dictionary, context_instance=context_instance))
