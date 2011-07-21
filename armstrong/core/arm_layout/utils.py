from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


def get_layout_template_name(model, name):
    return "layout/%s/%s/%s.html" % (
        model._meta.app_label,
        model._meta.object_name.lower(),
        name)


def render_object(object, name, dictionary=None, context_instance=None):
    dictionary = dictionary or {}
    dictionary["object"] = object
    return mark_safe(render_to_string(get_layout_template_name(object, name),
        dictionary=dictionary, context_instance=context_instance))



