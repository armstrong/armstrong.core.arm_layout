from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class BasicLayoutBackend(object):
    base_layout_directory = "layout"

    def get_layout_template_name(self, model_obj, name):
        ret = []
        for a in model_obj.__class__.mro():
            if not hasattr(a, "_meta"):
                continue

            ret.append("%s/%s/%s/%s.html" % (
                self.base_layout_directory,
                a._meta.app_label,
                a._meta.object_name.lower(),
                name))
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
