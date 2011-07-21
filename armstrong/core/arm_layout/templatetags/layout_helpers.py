from contextlib import contextmanager
import copy
from django import template
from django.template import RequestContext
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


def get_layout_template_name(model, name):
    return "layout/%s/%s/%s.html" % (
        model._meta.app_label,
        model._meta.object_name.lower(),
        name)


# TODO: This should live somewhere in armstrong.utils, just not sure where yet
@contextmanager
def sandboxed_context(context):
    context.push()
    yield
    context.pop()


class RenderObjectNode(template.Node):
    def __init__(self, object, name):
        self.object = template.Variable(object)
        self.name = name

    def render(self, context):
        with sandboxed_context(context):
            kwargs = {"dictionary": context, }
            if "request" in context:
                kwargs["context_instance"] = RequestContext(context["request"])

            object = self.object.resolve(context)
            context["object"] = object
            return mark_safe(render_to_string(get_layout_template_name(object,
                self.name), **kwargs))


@register.tag(name="render_object")
def do_render_object(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 3:
        _, object, name = tokens
        return RenderObjectNode(object, name)

    message = "Too %s parameters" % ("many" if len(tokens) > 3 else "few")
    raise TemplateSyntaxError(message)
